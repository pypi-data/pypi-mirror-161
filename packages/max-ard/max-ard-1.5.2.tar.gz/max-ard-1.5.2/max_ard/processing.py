"""Tools and utilities for processing ARD images

Provides
--------
- read/write windows from ARD collections
"""

from collections import deque
from typing import Any

from maxar_ard_grid import covers
from maxar_ard_grid.grid import get_CRS, get_transform
from shapely.geometry import shape
from shapely.ops import transform
from shapely.prepared import prep

from max_ard.dependency_support import HAS_RASTERIO
from max_ard.exceptions import MissingDependency
from max_ard.io import convert_to_shapely

if HAS_RASTERIO:
    import numpy as np
    import rasterio
    from rasterio import windows


__all__ = ("read_windows", "write_windows")


class COGReader:
    """An optimized COG rasterio reader

    ARD COGs do not have any sidecar files, therefore when opening
    we can use GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR' to skip looking
    for sidecar files. This skips an S3 LIST operation which takes
    time and money (LISTs cost more than READs).

    We also override some GDAL read settings for more potential speed
    and cost gains

    Parameters
    ----------
    path : str
        Path of COG to open
    *args : list
        Any additional args to pass to rasterio.open()
    **kwargs : dict
        Any additional keyword arguments to pass to rasterio.open()"""

    COG_ENV = {
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": True,
        "VSI_CACHE": True,
        "GDAL_HTTP_MULTIPLEX": True,
        "VRT_SHARED_SOURCE": 0,
    }

    def __init__(self, path, *args, **kwargs):
        with rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"
        ):
            self.dsr = rasterio.open(path, *args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        """Proxy to the underlying rasterio Dataset Reader"""
        if name == "read":

            def func(*args, **kwargs):
                with rasterio.Env(**COGReader.COG_ENV):
                    return self.dsr.read(*args, **kwargs)

            return func
        else:
            dsr = object.__getattribute__(self, "dsr")
            if name == "dsr":
                return dsr
            else:
                return getattr(dsr, name)

    # context manager dunders can't be proxied
    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.dsr.close()


def iterify(input):
    """Takes an input of any type and returns a list containing that input, if the input is not already an iterable or if it is a string.
    If the input is a non-string iterable, returns the input as is."""

    if isinstance(input, str):
        return [input]
    else:
        try:
            input[0]
            return input
        except:
            return [input]


def loop_geoms(collection, geoms, src_proj=4326):
    """Loops over a geometry source and emits a tuple of:
    - An ARDTile that overlaps a feature from the source
    - The feature as a Shapely geometry, reprojected to the tile's UTM projection

    Args:
        geoms: one or more geometry objects as:
            - Shapely geometry objects
            - dicts that follow the Python Geometry Interface (GeoJSON-like)
            - GeoJSON feature-like dicts that have a 'geometry' key
            - lists or tuples of above
            - a Fiona dataset reader
            - a path to a readable geometry file.

    Yields:
        tuple(ARDTile, shape): tuple of ARD Tile and reprojected Shapely geometry object"""

    src_crs = get_CRS(src_proj)

    geoms = convert_to_shapely(geoms)
    for geom in iterify(geoms):
        for cell in covers(geom, src_proj=src_proj):
            for tile in collection.get_stack(cell):
                tile_crs = get_CRS(tile.cell.proj)
                tfm = get_transform(src_crs, tile_crs)
                proj_geom = transform(tfm, geom)
                yield tile, proj_geom


def read_windows(collection, geoms, src_proj=4326):
    """A generator for reading windows from overlapping tiles in an ARDCollection

    Args:
        geoms: one or more geometry objects as:
            - Shapely geometry objects
            - dicts that follow the Python Geometry Interface (GeoJSON-like)
            - GeoJSON feature-like dicts that have a 'geometry' key
            - lists or tuples of above
            - a Fiona dataset reader
        src_proj: An EPSG identifier parseable by Proj4

    Yields:
        Tuple of:
            ARDTile of tile
            Shapely polygon representing the bounds of the input geometry
                in the tile's UTM coordinate system
            a Reader function:

                reader(asset)

                    Args:
                        asset(str): asset to read: `visual`, `pan`, or `ms`

                    Returns:
                        numpy array of data covered by the returned geometry

    Example:

    geoms = [...]
    for tile, geom, reader in read_windows(geoms):
        # can check tile.properties, or fetch tile.clouds
        # can check if `geom` intersects with clouds
        data = reader('visual')"""

    if not HAS_RASTERIO:
        raise MissingDependency("Rasterio is required to read ARD rasters")

    for tile, geom in loop_geoms(collection, geoms, src_proj):

        def reader(asset, **kwargs):
            dsr = tile.open_asset(asset)
            window = windows.from_bounds(*geom.bounds, dsr.transform)
            return dsr.read(window=window, **kwargs)

        yield (tile, geom, reader)


def write_windows(collection, geoms, src_proj=4326):

    if not HAS_RASTERIO:
        raise MissingDependency("Rasterio is required to read ARD rasters")

    for tile, geom in loop_geoms(collection, geoms, src_proj):

        def writer(asset, name, **kwargs):
            dsr = tile.open_asset(asset)
            window = windows.from_bounds(*geom.bounds, dsr.transform)
            profile = dsr.meta
            profile.update(
                {
                    "width": window.width,
                    "height": window.height,
                    "count": dsr.count,
                    "transform": dsr.window_transform(window),
                    "driver": "GTiff",
                }
            )
            profile.update(kwargs)
            with rasterio.open(name, "w", **profile) as dest:
                dest.write(dsr.read(window=window))

        yield (tile, geom, writer)


class AcquisitionReader:
    """A pixel reader that reads across tiles in an acquisition.

    Default behavior is to histogram match pixels from different tiles to match
    the tile that represents the majority of pixels in the window.

    NOTE: experimental and not production tested!

          Will have problems with acquisitions that span UTM zones.

          This can be probably be fixed with rasterio.warpedVRTs but
          will take more work if there's demand for this feature.

    Parameters
    ----------
    acquisition: max_ard.Acquisition
        Acquisition object"""

    def __init__(self, acquisition):
        # store the tile cell bounds as prepared geoms
        # for intersection
        if not HAS_RASTERIO:
            raise MissingDependency("Rasterio is required for pixel reading")
        self.cells = {tile: prep(shape(tile.cell)) for tile in acquisition}

    def read(self, aoi, asset, src_proj=4326, match=True):
        """Read an AOI window from an asset type

        Parameters
        ----------
        aoi: almost any geometry input
            Window to read, will use this geometry's envelope if not rectilinear.

        asset: str
            Asset name, currently 'visual', 'pan', 'ms;

        match: bool, optional
            Whether to apply histogram matching.

        Returns
        -------
        ndarrary
            Array of image data"""

        # Priority in the image goes to the source tile with the most pixels
        # Calculate overlapping areas for tiles and sort biggest to smallest
        candidates = []
        src_crs = get_CRS(src_proj)

        aoi = convert_to_shapely(aoi)

        for tile, geom in self.cells.items():
            tile_crs = get_CRS(tile.cell.proj)
            tfm = get_transform(src_crs, tile_crs)
            proj_aoi = transform(tfm, aoi)
            # if a cell contains the AOI just return it
            if geom.contains(proj_aoi):
                return self.read_aoi(tile, asset, proj_aoi)[0]
            elif geom.intersects(proj_aoi):
                candidates.append((tile, shape(tile.cell).intersection(proj_aoi).area))
        if len(candidates) == 0:
            raise ValueError("AOI does not intersect any tiles")
        # we need to grab the biggest first, then insert based on area
        candidates.sort(key=lambda x: x[1])
        candidates = deque(candidates)
        candidates.rotate(1)

        output = None
        reference = None
        # Loop through sources and insert into output array
        for tile, area in candidates:
            array, window = self.read_aoi(tile, asset, proj_aoi)
            bands, height, width = array.shape
            if output is None:
                output = np.zeros(
                    (bands, int(round(window.height)), int(round(window.width))), array.dtype
                )

            if window.col_off < 0:
                col_off = -int(round(window.col_off))
            else:
                col_off = 0
            if window.row_off < 0:
                row_off = -int(round(window.row_off))
            else:
                row_off = 0
            # first loop grabs the reference (biggest) image
            if reference is None:
                reference = array
                reference_position = (row_off, col_off, height, width)
            else:
                if match:
                    array = self.histogram_match(array, reference)
                output[:, row_off : row_off + height, col_off : col_off + width] = array

        # insert the reference back on top
        row_off, col_off, height, width = reference_position
        output[:, row_off : row_off + height, col_off : col_off + width] = reference
        return output

    def read_aoi(self, tile, asset, aoi):
        """Read an AOI from a tile

        Parameters
        ----------
        tile: max_ard.ARDTile
            Tile to read from

        asset: str
            Asset name, currently 'visual', 'pan', 'ms;

        aoi: Shapely geometry
            Window to read, will use this geometry's envelope if not rectilinear.
            Must be in UTM to match the acquisition (also see notes above)


        match: bool, optional
            Whether to apply histogram matching.

        Returns
        -------
        ndarrary
            Array of image data"""

        source = tile.open_asset(asset)
        window = windows.from_bounds(*aoi.bounds, source.transform)
        return (source.read(window=window), window)

    def histogram_match(self, source, template):
        """Adjust the pixel values of an image such that its histogram
        matches that of a target image.

        from
        https://gist.github.com/jcjohnson/e01e4fcf7b7dfa9e0dbee6c53d3120b6)

        Code adapted from
        http://stackoverflow.com/questions/32655686/histogram-matching-of-two-images-in-python-2-x

        Parameters
        ----------
        source: np.ndarray
            Image to adjust
        template: np.ndarray
            Template image; can have different dimensions to source

        Returns
        -------
        np.ndarray
            The transformed output image"""

        oldshape = source.shape
        source = source.ravel()
        template = template.ravel()

        # get the set of unique pixel values and their corresponding indices and
        # counts
        s_values, bin_idx, s_counts = np.unique(source, return_inverse=True, return_counts=True)
        t_values, t_counts = np.unique(template, return_counts=True)

        # take the cumsum of the counts and normalize by the number of pixels to
        # get the empirical cumulative distribution functions for the source and
        # template images (maps pixel value --> quantile)
        s_quantiles = np.cumsum(s_counts).astype(np.float64)
        s_quantiles /= s_quantiles[-1]
        t_quantiles = np.cumsum(t_counts).astype(np.float64)
        t_quantiles /= t_quantiles[-1]

        # interpolate linearly to find the pixel values in the template image
        # that correspond most closely to the quantiles in the source image
        interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

        return interp_t_values[bin_idx].reshape(oldshape)
