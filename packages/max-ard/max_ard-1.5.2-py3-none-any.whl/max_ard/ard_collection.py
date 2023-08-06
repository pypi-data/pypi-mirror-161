"""Collection objects representing stored ARD data

Provides
--------
  1. Connect to local or cloud ARD tiles
  2. Filter collections of tiles
  3. Furter iterate over collection of tiles spatially or temporally
  4. Pythonic access of ARD images and masks

Reference
---------

SDK Ordering Tutorial

- https://ard.maxar.com/docs/sdk/sdk/ordering-ard/


Example
-------
>>> collection = ARDCollection('bucket/prefix')
>>> for tile in collection.tiles:
        print tile.cell.bounds

"""

import json
import os
import re
import warnings
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path, PurePosixPath
from posixpath import join as urljoin
from typing import Any, Iterable, List, Optional, Union
from urllib.parse import urlparse

from fsspec import filesystem
from fsspec.implementations.local import LocalFileSystem
from fsspec.spec import AbstractFileSystem
from maxar_ard_grid import Cell, covers
from shapely.geometry import GeometryCollection, mapping, shape, box

from max_ard.base_collections import BaseCollection
from max_ard.dependency_support import HAS_FIONA, HAS_RASTERIO
from max_ard.exceptions import MissingDependency, NotFinished
from max_ard.order import Order
from max_ard.processing import COGReader, read_windows, write_windows

# Optional dependencies


if HAS_RASTERIO:
    import rasterio
if HAS_FIONA:
    import fiona


class ARDTile:
    """Represents an ARD Tile - the images and vectors from one acquistion in one grid cell

    These objects have dynamic accessors for assets - calling the asset name (with underscores substituted
    for dashes) is the same as calling `ARDTile.open_asset(<name>)`.

    Example: `ARDTile.visual` returns a Rasterio dataset reader of the `visual` raster asset.

    Vector assets can also be accessed "inverted" by prefixing `no_` to the asset name.

    Example: `ARDTile.no_cloud_mask` will return the geometry of areas *not* covered by clouds.
    """

    # matching regexes
    # don't be a smartass and combine them

    # matches quadkeys
    CELL_REGEX = re.compile(r"[/-](\d{2})[-/]([0123]{12})[/-]")
    # matches regular catalog IDs
    CAT_ID_REGEX = re.compile(r"10[1-6][0AC][0-9A-F]{3}0[0-9A-F]{6}00", re.I)
    # matches WV4 catIDs (UUID v4)
    WV4_REGEX = re.compile(
        r"([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}-inv)", re.I
    )
    # matches dates yyyy-mm-dd
    DATE_REGEX = re.compile(r"\d{4}-\d{2}-\d{2}")

    def __init__(self) -> None:
        self.date = None  #: date of cell

        #: acquisition ID
        self.acq_id = None
        self.quadkey = None
        """ ARD Grid quadkey of the tile's cell """
        self.zone = None
        """ UTM zone of the tile """

    @property
    def properties(self) -> dict:
        """metadata of the ARD tile"""
        return self.stac_item["properties"]

    def __getattr__(self, name: str) -> Any:
        if name == "clouds":
            warnings.warn("clouds attribute should be accessed with ARDTile.cloud_mask")
            return self.open_asset("cloud-mask")
        elif name == "extent":
            warnings.warn("extent attribute should be accessed with ARDTile.data_mask")
            return self.open_asset("data-mask")
        elif name == "nodata":
            warnings.warn("clouds attribute should be accessed with ARDTile.no_data_mask")
            return shape(self.cell).difference(self.data_mask)
        elif name.startswith("no_"):
            asset_name = name.split("_", 1)[1].replace("_", "-")
            source = getattr(self, asset_name)
            try:
                source.area
            except:
                raise AttributeError(
                    f"Attribute {name} is not spatial so it can't be flipped with 'no_'"
                )
            if name == "no_data_mask":
                return box(*self.visual.bounds).difference(source)
            else:
                return self.data_mask.difference(source)
        else:
            asset_name = name.replace("_", "-")
            if asset_name in self.asset_paths:
                return self.open_asset(asset_name)
            else:
                raise AttributeError(f"Attribute .{name} not found")

    @property
    @lru_cache()
    def cell(self) -> Cell:
        """The ARD Grid cell of the tile"""
        return Cell(self.quadkey, zone=self.zone)

    @classmethod
    def from_doc(cls, fs: AbstractFileSystem, path: str):
        """
        Create an ARDTile object from a path to any of a tile's files.

        Parameters
        ----------
        fs : fsspec.AbstractFileSystem
           a `filesystem` object used to read files.
        path : str
            a path to any file in a tile.

        Returns
        -------
        ARDTile
        """

        tile = cls()
        tile.fs = fs

        # zone and quadkey
        try:
            matches = ARDTile.CELL_REGEX.search(path)
            tile.zone = matches[1]
            tile.quadkey = matches[2]

            # cat ID
            matches = ARDTile.CAT_ID_REGEX.search(path)
            if matches is None:
                matches = ARDTile.WV4_REGEX.search(path)
            tile.acq_id = matches[0]

            # date
            matches = ARDTile.DATE_REGEX.search(path)
            tile.date = matches[0]

        except IndexError:
            # use index error to find when we can't match a needed field
            raise ValueError("Non-conforming data found, please contact ard-support@maxar.com")

        # prefixes for opening files with gdal/ogr

        if "s3" in tile.fs.protocol:
            tile.gdal_prefix = f"/vsis3/"
        elif "gs" in tile.fs.protocol:
            tile.gdal_prefix = f"/vsigs/"
        elif "az" in tile.fs.protocol:
            tile.gdal_prefix = f"/vsiaz/"
        else:
            tile.gdal_prefix = ""

        # rebuild the path from properties
        # might be overkill
        base_prefix = path.split(f"/{tile.zone}/{tile.quadkey}")[0]
        base_prefix = urljoin(base_prefix, tile.zone, tile.quadkey)
        # legacy canvas
        if tile.date is not None:
            base_prefix = urljoin(base_prefix, tile.date)
        else:
            warnings.warn(
                "Legacy Canvas file path without date - this will not be supported in the future"
            )
        tile.base_prefix = base_prefix

        return tile

    @property
    @lru_cache()
    def stac_item(self) -> dict:
        item = f"{self.base_prefix}/{self.acq_id}.json"
        with self.fs.open(item) as f:
            return json.load(f)

    class AssetPaths(dict):
        """A dictionary that warns when old asset names are called
        The names will get deprecated at some point"""

        def __getitem__(self, key):
            if key == "clouds":
                warnings.warn(
                    'The "clouds" asset has been renamed to "cloud-mask", please update your call'
                )
            if key == "extent":
                warnings.warn(
                    'The "extent" asset has been renamed to "data-mask", please update your call'
                )
            return dict.__getitem__(self, key)

    @property
    @lru_cache()
    def asset_paths(self) -> AssetPaths:
        # TODO set a way to specify this so we don't have to check the stac every time
        # given a homogenous dataset

        assets = ARDTile.AssetPaths()

        # Item isn't a true STAC asset but we treat it as an asset of the ARDTile
        # we could also treat this as "self" but that's not as clear
        assets["item"] = f"{self.base_prefix}/{self.acq_id}.json"

        # once STAC sample data is fixed, we can pull the assets from the Item
        # then we can add new assets without updating the SDK
        stac_assets = self.stac_item["assets"]

        # old non-relative links
        if stac_assets["visual"]["href"].startswith("s3://"):
            assets["visual"] = f"{self.base_prefix}/{self.acq_id}-visual.tif"
            assets["pan"] = f"{self.base_prefix}/{self.acq_id}-pan.tif"
            assets["ms"] = f"{self.base_prefix}/{self.acq_id}-ms.tif"
            assets["cloud-mask"] = f"{self.base_prefix}/{self.acq_id}-cloud-mask.gpkg"
            assets["data-mask"] = f"{self.base_prefix}/{self.acq_id}-data-mask.gpkg"
        else:
            # use stac asset hrefs
            for name, asset in stac_assets.items():
                if type(self.fs) == LocalFileSystem:
                    assets[name] = str(Path(self.base_prefix) / Path(asset["href"]))
                else:
                    assets[name] = str(PurePosixPath(self.base_prefix) / Path(asset["href"]))

        # legacy naming
        assets["clouds"] = assets["cloud-mask"]
        assets["extent"] = assets["data-mask"]
        return assets

    def __repr__(self):
        return f"<ARDTile of {self.acq_id} at z{self.zone}-{self.quadkey}>"

    # there's a small speed boost plus some cost savings with GETs by caching
    # asset fetching
    @lru_cache(maxsize=16)
    def open_asset(self, name):
        """
        Open an asset by name, where `name` is a key in the STAC Item assets

        For information on the asset files see https://ard.maxar.com/docs/ard_order_delivery/about_ard_order_delivery/

        To open the tile STAC Item itself, use 'item'.
        Current values for ARD V3 are:

        STAC metadata:
        - item

        Vectors:
        - cloud-mask
        - cloud-shadow-mask
        - terrain-shadow-mask
        - ms-saturation-mask
        - data-mask

        Rasters:
        - visual
        - pan
        - ms
        - clouds
        - ms-saturation
        - terrain-shadows
        - water

        Vectors returned will be a single Shapely geometry object, a GeometryCollection of multiple objects, or if
        the mask is empty an empty GeometryCollection.

        Parameters
        ----------
        name : str
            name of asset to open, see list above

        Returns
        -------
        rasterio.DataSetReader
            for raster assets or
        shapely.geometry
            for vector assets or
        dict
            for STAC Items (JSON)
        """

        asset = self.asset_paths[name]
        if asset.endswith("tif"):
            if not HAS_RASTERIO:
                raise MissingDependency("Rasterio is required to read ARD rasters")
            # return rasterio.open(f'{self.gdal_prefix}{asset}')
            return COGReader(f"{self.gdal_prefix}{asset}")

        if asset.endswith("geojson") or asset.endswith("gpkg"):
            if not HAS_FIONA:
                raise MissingDependency("Fiona is required to access ARD masks as geometries")
            with fiona.open(f"{self.gdal_prefix}{asset}") as layer:
                geom = [shape(f["geometry"]) for f in layer]
            if len(geom) == 1:
                return geom[0]
            elif len(geom) == 0:
                return GeometryCollection()
            else:
                return GeometryCollection(geom)

        if asset.endswith("json"):
            with self.fs.open(asset) as f:
                return json.load(f)

    @property
    def __geo_interface__(self):
        """Python Geospatial Interface of tile's valid pixels"""
        return mapping(self.data_mask)


class ARDCollection(BaseCollection):
    """ARDCollections represent collections of S3 tiles. Currently the tiles
    can be stored in S3 or locally.

    Parameters
    ----------
    path : str
        Path to S3 prefix or STAC collection.
    aoi : shapely.geometry or str, optional
        Limit to finding tiles that cover this AOI, can be shapely geometry or most textual representations.
    acq_id_in : iterable of str, optional
        Limit to finding tiles from these acquisitions.
    zone_in : iterable of int, optional
        Limit to finding tiles in these zones.
    earliest_date : str or datetime.date or datetime.datetime, optional
        Limit to finding tiles after this date (strings must be YYYY-MM-DD).
    latest_date : str or datetime.date or datetime.datetime, optional
        Limit or finding tiles before this date.
    profile : str, optional
        AWS Profile to use when tiles are in S3.
    public : bool
        Access cloud data without authentication (for public buckets).


    The following parameters are also settable attributes and will trigger a rescan

    Attributes
    ----------
    path
    aoi
    acq_id_in
    zone_in
    earliest_date
    latest_date
    """

    def __init__(
        self,
        path: str,
        aoi: Optional[Any] = None,
        acq_id_in: Optional[Iterable[str]] = None,
        zone_in: Optional[Iterable[int]] = None,
        earliest_date: Optional[Union[str, datetime, date]] = None,
        latest_date: Optional[Union[str, datetime, date]] = None,
        profile: Optional[str] = None,
        public: Optional[bool] = False,
        **kwargs,
    ) -> None:

        self._dirty = True
        self._updating = False
        super().__init__()

        # TODO we may want to normalize AOIs to WGS84
        # but right now `covers` is probably capable enough
        self.aoi = aoi

        # disable authentication for public buckets
        # 'anon' is what fsspec calls it but 'public' makes more sense
        if public or kwargs.get("anon") == True:
            anon = True
            os.environ["AWS_NO_SIGN_REQUEST"] = "YES"
        else:
            anon = False

        # validate some inputs that have been problematic in the past
        assert zone_in is None or all(type(z) == int for z in zone_in), "Zones must be integers"
        if not zone_in:
            zone_in = None
        self.zone_in = zone_in

        assert acq_id_in is None or all(
            type(c) == str for c in acq_id_in
        ), "Catalog IDs must be strings"
        if not acq_id_in:
            acq_id_in = None
        self.acq_id_in = acq_id_in

        # store dates as strings, reformat if needed
        def format_date(d):
            if d is None:
                return None
            try:
                return d.strftime("%Y-%m-%d")
            except:
                assert re.match(
                    r"\d{4}-\d{2}-\d{2}", d
                ), "Dates must be YYYY-MM-DD strings, or date/datetime objects"
                return d

        self.earliest_date = format_date(earliest_date)
        self.latest_date = format_date(latest_date)

        # Set up the path and initialize the filesystem source
        self.path = path

        # this might need to be smarter (os.path?) for windows slashes
        if self.path[-1] == "/":
            self.path = self.path[:-1]
        if os.path.exists(self.path):
            self.storage_type = "file"
            self.fs_path = os.path.abspath(self.path)
        else:
            parsed = urlparse(self.path)
            if parsed.scheme == "":
                raise ValueError("Local path does not exist")
            if parsed.scheme not in ["s3", "gs", "az"]:
                raise ValueError("Unrecognized protocol (use s3://, gs://, or az://")
            self.storage_type = parsed.scheme
            # might not need this, s3fs doesn't care about paths leading with protocols
            # need to check gdal, etc
            self.fs_path = parsed.netloc + parsed.path

        self.fs = filesystem(self.storage_type, anon=anon, profile=profile)

        try:
            self.fs.ls(self.path)
        except:
            raise ValueError("Access error: check your path for errors and access permissions")

    def __setattr__(self, name, value):
        """Some attributes are read-only properties
        Related setters need to reset the collection state"""

        if name == "acq_ids":
            raise ValueError(".acq_ids is read-only - set .acq_id_in instead")
        if name == "zones":
            raise ValueError(".zones is read-only - set .zone_in instead")
        if name == "start_date":
            raise ValueError(".start_date is read-only - set .earliest_date instead")
        if name == "acq_ids":
            raise ValueError(".end_date is read-only - set .latest_date instead")
        if name in ["acq_id_in", "zone_in", "earliest_date", "latest_date", "aoi"]:
            # resets the bins
            self._dirty = True
        object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        dirty = object.__getattribute__(self, "_dirty")
        updating = object.__getattribute__(self, "_updating")
        if (
            dirty
            and not updating
            and name
            in [
                "tiles",
                "acquisitions",
                "acquisition_ids",
                "stacks",
                "cells",
                "get_stack",
                "get_acquisition",
                "dates",
                "earliest_date",
                "latest_date",
                "zones",
                "read_windows",
                "write_windows",
            ]
        ):
            object.__setattr__(self, "_updating", True)
            self._scan_files()
            object.__setattr__(self, "_dirty", False)
            object.__setattr__(self, "_updating", False)
        return object.__getattribute__(self, name)

    def __repr__(self) -> str:
        return f"<ARDCollection at {self.path}/>"

    def _scan_files(self) -> None:
        self._reset()

        if self.aoi is not None:
            cells = set([f"{c.zone}/{c.quadkey}" for c in covers(self.aoi)])
        else:
            cells = []

        # STAC source
        if self.path.endswith("json"):

            with self.fs.open(self.path) as f:
                doc = json.load(f)

            # STAC Item
            if "type" in doc.keys():
                items = [self.path]

            # STAC Collection
            else:
                root_path = self.fs_path.split("order_collections")[0]
                items = []
                for link in doc["links"]:
                    if link["rel"] != "child":
                        continue
                    path = root_path + link["href"].replace("../", "")
                    with self.fs.open(path) as f:
                        links = json.load(f)["links"]
                        for link in links:
                            if link["rel"] == "item":
                                path = root_path + link["href"].replace("../", "")
                                items.append(path)

        # Filesystem source
        else:
            # build leading glob pattern based on zone & quadkey
            if self.aoi is not None:
                # shard on first 5 digits on quadkey
                # for parallel fetches
                qkbs = set()
                for qk in cells:
                    qkbs.add(qk[:5])
                paths = [f"{k}*/*/*.json" for k in qkbs]
            else:
                if not self.zone_in or len(self.zone_in) == 0:
                    paths = ["*/*/*/*.json"]
                else:
                    paths = [f"{z}/*/*/*.json" for z in self.zone_in]
            items = []
            for path in paths:
                full_path = f"{self.path}/{path}"
                for item in self.fs.glob(full_path):
                    items.append(item)

        # Filter out items
        for item in items:
            tile = ARDTile.from_doc(self.fs, item)
            if self.aoi is not None:
                if f"{tile.zone}/{tile.quadkey}" not in cells:
                    continue
            if self.acq_id_in is not None and tile.acq_id not in self.acq_id_in:
                continue
            if self.earliest_date is not None:
                if tile.date < self.earliest_date:
                    continue
            if self.latest_date is not None:
                if tile.date > self.latest_date:
                    continue
            self.add_tile(tile)

    def clear_filesystem_cache(self):
        """
        Clear the local cache of a remote filesystem

        Remote file systems (S3, Azure, Google Cloud) cache files locally for speed.
        If the remote files have changed while using an ARDCollectino, you can clear
        the cached files so that new files will be loaded.

        Parameters
        ----------

        Returns
        -------
        """
        self.fs.clear_instance_cache()

    @classmethod
    def from_order(cls, order, **kwargs):
        """
        Create an ARDCollection from an order ID.

        Accepts all filter keywords as used by class initialization.

        Parameters
        ----------
        order_id : str or Order
            Order object or Order ID to open.
        **kwargs
            Filter keywords as used by class initialization.

        Returns
        -------
        ARDCollection
        """

        if type(order) == str:
            order = Order.from_id(order)
        if not order.finished:
            raise NotFinished

        output_config = order.response.order.output_config
        if "bucket" in output_config:
            bucket = output_config["bucket"]
            prefix = output_config["prefix"]
            protocol = "s3"
        elif "amazon_s3" in output_config:
            bucket = output_config["amazon_s3"]["bucket"]
            prefix = output_config["amazon_s3"]["prefix"]
            protocol = "s3"
        elif "google_cloud_storage" in order:
            bucket = output_config["google_cloud_storage"]["bucket"]
            prefix = output_config["google_cloud_storage"]["prefix"]
            protocol = "gs"
        elif "azure_blob_storage" in order:
            bucket = output_config["azure_blob_storage"]["container"]
            prefix = output_config["azure_blob_storage"]["prefix"]
            protocol = "az"
        path = f"{protocol}://{bucket}/{prefix}/order_collections/{order.order_id}_root_collection.json"
        self = cls(path, **kwargs)
        return self

    def read_windows(self, *args, **kwargs):
        """See `max_ard.processing.read_windows`"""
        return read_windows(self, *args, **kwargs)

    def write_windows(self, *args, **kwargs):
        """See `max_ard.processing.write_windows`"""
        return write_windows(self, *args, **kwargs)


def copy(
    collection: ARDCollection, destination: str, flatten: bool = False, dry_run: bool = False
) -> None:
    """Copy data from a collection to a local location

    Parameters
    ----------
    collection : ARDCollection
        The ARDCollection to copy locally.
    destination : str
        Local path to copy to.
    flatten : bool False
        Write files in flat format without subdirectories.
    dry_run : bool False
        Print the source and destination of files instead of copying.

    Returns
    -------
    None
    """

    Path(destination).mkdir(parents=True, exist_ok=True)
    for tile in collection.tiles:
        paths = tile.asset_paths.copy()
        # legacy names
        try:
            del paths["clouds"]
            del paths["extent"]
        except:
            pass
        for path in paths.values():
            source = path
            target = path.replace(collection.fs_path, "")[1:]
            if flatten:
                target = urljoin(destination, target.replace("/", "-"))
            else:
                target = urljoin(destination, target)
            if dry_run:
                print(source, target)
            else:
                if not flatten:
                    Path(target).parent.mkdir(parents=True, exist_ok=True)
                collection.fs.get(source, target)
