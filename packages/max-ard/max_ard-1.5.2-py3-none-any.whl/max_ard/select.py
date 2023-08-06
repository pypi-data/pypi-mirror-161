"""Create ARD Selects and view results

Provides
--------
  1. Objects representing Selects
  2. Objects representing detailed results of a Select


Documentation
-------------

Select API Overview

- https://ard.maxar.com/docs/select-and-order/select-tiles/

Select SDK Tutorial

- https://ard.maxar.com/docs/sdk/sdk/selecting-ard/

API request and response examples

- https://ard.maxar.com/docs/api-reference/select/select_resource/

Example
-------

    >>> bbox = [-106.8, 35.1, -106.4, 35.4]
    >>> datetime =  "2020-07-01T00:00:00Z/2021-01-25T00:00:00Z"
    >>> query = {
            "platform": {
            "eq": "worldview-02"
            },
            "aoi:cloud_free_percentage": {
            "gte": 95
            },
            "aoi:data_percentage": {
            "gte": 75
            }
        }
    >>> select = Select(datetime=datetime, bbox=bbox, query=query, stack_depth=3)
    >>> select.submit()
    >>> s.state
    SUCCEEDED
    >>> s.select_id
    5629729628519955012
    >>> s.usage
    SelectUsage(
        area=UsageArea(fresh_imagery_sqkm=0.0, standard_imagery_sqkm=2317.0, training_imagery_sqkm=0.0, total_imagery_sqkm=2317.0, estimate=True), 
        cost=UsageCost(fresh_imagery_cost=0.0, standard_imagery_cost=24.0, training_imagery_cost=0.0, total_imagery_cost=24.0, estimate=True), 
        limits=UsageLimits(limit_sqkm=-1.0, fresh_imagery_fee_limit=-1.0, standard_imagery_fee_limit=-1.0, training_imagery_fee_limit=-1.0, annual_subscription_fee_limit=-1.0), 
        available=UsageAvailable(available_sqkm=-1.0, fresh_imagery_balance=-1.0, standard_imagery_balance=-1.0, training_imagery_balance=-1.0, total_imagery_balance=-1.0), 
        usage_as_of='2021-07-27T18:29:11Z')
    >>> results = s.results
    >>> print(results)
    <SelectResult (95 tiles in 12 acquisitions) >
    >>> results.dates
    ['2020-07-10',
    '2020-07-24',
    '2020-07-29',
    '2020-09-08',
    '2020-10-21',
    '2021-01-16']
 
"""
import json
import warnings
from functools import lru_cache, wraps
from math import cos, radians
from pathlib import Path
from time import sleep
from typing import List, Union

import requests
from maxar_ard_grid import Cell
from pydantic import BaseModel
from shapely.geometry import LineString, Point, Polygon, box, mapping, shape
from shapely.wkt import loads

from max_ard.admin import AdminUsage
from max_ard.base_collections import ARDModel, BaseCollection, Succeeded, Submitted
from max_ard.exceptions import (
    ARDServerException,
    BadARDRequest,
    NotFinished,
    NotSubmitted,
    SelectError,
)
from max_ard.io import KmlDoc, ShpDoc, convert_to_shapely
from max_ard.session import ard_url, get_user_session

__all__ = ("Select", "SelectResult", "SelectTile")


class SelectRequest(ARDModel):
    """An object to hold the request to the Select Service"""

    ids: List[str] = None
    datetime: str = None
    stack_depth: int = None
    intersects: Union[str, dict] = None
    bbox: Union[List, tuple] = None
    query: dict = {}
    image_age_category: Union[List, tuple] = None

    class Config:
        extra = "allow"
        validate_assignment = True


class SelectUsage(AdminUsage):
    """Model to hold usage information returned from a Select

    Inherits from AdminUsage, however this adds a 'usage_as_of' field so that Select products
    that show this information can indicate that the account balance was valid when the Select was run.

    """

    usage_as_of: str

    def __getitem__(self, key):
        """Get old usage values for backwards compatibility"""
        warnings.warn(
            "Usage objects are now Pydantic models with more fields, simple dict access will be deprecated",
            DeprecationWarning,
        )
        if key == "limit_sqkm":
            return self.limits.limit_sqkm
        elif key == "available_sqkm":
            return self.available.available_sqkm
        elif key == "usage_as_of":
            return self.usage_as_of
        elif key == "fresh_imagery_sqkm":
            return self.area.fresh_imagery_sqkm
        elif key == "standard_imagery_sqkm":
            return self.area.standard_imagery_sqkm
        elif key == "selection_sqkm":
            return self.area.total_imagery_sqkm
        elif key == "training_imagery_sqkm":
            return self.area.training_imagery_sqkm
        else:
            raise KeyError()


class SelectResponse(BaseModel):
    """an object to hold the Select API response"""

    id: str
    status: str
    request_details: dict = None
    stack_depth_summary: dict = None
    unique_acquisitions: int = None
    usage: SelectUsage = None
    links: dict = None
    error_message: dict = None

    class Config:
        extra = "allow"
        allow_mutation: False


class Select(Succeeded, Submitted):
    """An ARD API Select object

    Parameters
    ----------
    acq_ids : iterable of str
        An iterable of acquisition IDs to search for
    datetime : str
        Date or date range string
    intersects : Geometry-like objects, str (optional))
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric
        Bounding box in WGS84 coordinates, [west, south, east, north]
    query : dict
        Query dictionary
    stack_depth: int or None, optional
        Maximum number of tiles to return
    image_age_category : iterable of str, optional
        One or
    session : session object, optional
        A user_session or application_session object

    Attributes
    ----------
    session : session object or None
        A user_session or application_session object
    submitted : bool
        True if Select has been submitted via `max_ard.select.Select.submit`
    request : Pydantic model
        Parameters are loaded into a Pydantic model of the HTTP API request
    response : Pydantic model
        Pydantic model of the server response to API call. Status and submit calls
        return the same payload


    Notes
    -----

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading"""

    # store an authenticated Requests session in the class

    def __init__(
        self,
        acq_ids=None,
        datetime=None,
        intersects=None,
        bbox=None,
        query={},
        stack_depth=None,
        image_age_category=None,
        session=None,
    ):

        self.session = session or get_user_session()

        if intersects is not None:
            intersects = convert_to_shapely(intersects).wkt

        self.request = SelectRequest(
            ids=acq_ids,
            datetime=datetime,
            intersects=intersects,
            bbox=bbox,
            stack_depth=stack_depth,
            query=query,
            image_age_category=image_age_category,
        )
        self.response = None

    @property
    def submitted(self):
        if self.response:
            return self.response.id is not None
        else:
            return False

    @property
    @Submitted.required
    def running(self):
        """The Select is currently running"""

        return self.status == "RUNNING"

    @property
    @Submitted.required
    def finished(self):
        """The Select has finished running but may have failed"""

        return self.status != "RUNNING"

    @property
    @Submitted.required
    def succeeded(self):
        """The Select has finished running and has succeeded"""

        return self.status == "SUCCEEDED"

    @property
    @Submitted.required
    def failed(self):
        """The Select has finished running but has failed"""

        return self.status in ["FAILED", "ERROR"]

    @Submitted.required
    def wait_for_success(self, interval: int = 5) -> None:
        """Wait for the Select to succeed

        Parameters
        ----------
        interval: numeric, optional
            polling interval for success, default is 5 secs

        Raises
        ------
        SelectError
            An error in the selection caused it to fail"""

        while self.status == "RUNNING":
            sleep(interval)
        if self.status == "FAILED":
            error = self.response.error_message
            msg = f'{error["Error"]}: {error["Cause"]}'
            raise SelectError(msg)

    @property
    @Submitted.required
    def status(self):
        """Status of the select process: 'RUNNING', 'FINISHED', or 'FAILED'"""
        if self.response.status == "RUNNING":
            response = self.get_select(self.select_id, self.session)
            self.response = SelectResponse(**response)
        return self.response.status

    @property
    def state(self):
        """Alternate name for `max_ard.Select.status`, will be deprecated"""
        return self.status

    @property
    @Submitted.required
    def select_id(self):
        """ID of the Select"""

        return self.response.id

    @property
    @Succeeded.required
    def usage(self):
        """Dictionary of data usage metrics"""

        return self.response.usage

    @classmethod
    def from_id(cls, select_id: str, session=None):
        """Create a Select object from an ID

        Parameters
        ----------
        select_id: str
            Select ID to hydrate into a Select object
        session : Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        Select"""

        if not session:
            session = get_user_session()
        instance = cls()
        instance.session = session
        response = cls.get_select(select_id, session)
        instance.response = SelectResponse(**response)
        if "request_details" in response:
            instance.request = SelectRequest(**response["request_details"])
        return instance

    @classmethod
    def get_select(cls, select_id, session=None):
        """Fetch raw data about a Select from an ID

        Parameters
        ----------
        select_id : str
            Select ID to fetch metadata for
        session: Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        dict
            API data for the given Select"""

        if not session:
            session = get_user_session()

        r = session.get(ard_url("select", "request", select_id))
        return r.json()

    @classmethod
    def send_select(cls, payload, session=None):
        """Send a request to the Select API

        Parameters
        ----------
        payload : dict
            Select API request payload
        session : Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        dict
            API response data for the given Select"""

        if not session:
            session = get_user_session()
        r = session.post(ard_url("select"), json=payload)
        return r.json()

    def submit(self):
        """Submit this Select to the API"""

        response = self.send_select(self.request.to_payload(), self.session)
        if self.submitted:
            warnings.warn("The Select has already been submitted")
            return
        self.response = SelectResponse(**response)
        # update request in case defaults were applied
        self.request = SelectRequest(**self.response.request_details)

    @lru_cache()
    @Succeeded.required
    def get_link_contents(self, name):
        """Get the contents of an Select result file via its signed link

        Parameters
        ----------
        name : str
            The Select result file name

        Returns
        -------
        str
            Link contents"""

        temp_url = self.get_signed_link(name)
        # unauthenticated, don't send token
        r = requests.get(temp_url)
        r.raise_for_status()
        return r.text

    @Succeeded.required
    def get_signed_link(self, name):
        """Get the signed link for a Select result file

        Parameters
        ----------
        name : str
            The Select result file name

        Returns
        -------
        str
            signed URL"""

        url = self.response.links[name]
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()["download_link"]

    @Succeeded.required
    def copy_file(self, name, dir="."):
        """Copy a Select result file to a local location

        Parameters
        ----------
        name : str
            The Select result file name
        dir : str, optional
            Local directory location to copy to, file will retain its name"""

        # TODO get the output filename
        path = Path(dir, f"{self.select_id}.{name}")

        with open(path, "w") as out:
            file = self.get_link_contents(name)
            out.write(file)

    @property
    @lru_cache()
    @Succeeded.required
    def results(self):
        """The results of a select converted to Python objects"""

        return SelectResult.from_geojson(json.loads(self.get_link_contents("geojson")))

    def __repr__(self) -> str:
        if not self.submitted:
            return f"<ARD Select (unsubmitted)>"
        elif self.succeeded:
            return f"<ARD Select {self.select_id}>"
        else:
            return f"<ARD Select ({self.status})>"


class SelectTile:
    """An ARD tile identified in material selection

    These are generated by the SelectResult hydration and would not be initalized independently

    Parameters
    ----------
    properties : dict
        The properties of the source tile

    Attributes
    ----------
    date : str
        Date of object as YYYY-MM-DD string
    acq_id : str
        Acquisition ID of tile source
    quadkey : str
        Quadkey of the tile
    zone : int
        UTM zone of the tile
    cell_id : str
        Cell ID, example Z13-031133320001"""

    def __init__(self, properties: dict):
        self.properties = properties
        self.date = self.properties["date"]
        self.acq_id = self.properties["acquisition_id"]
        self.quadkey = self.properties["tile:quadkey"]
        self.zone = int(self.properties["tile:zone"])
        self.cell_id = "Z%02d-%s" % (self.zone, self.quadkey)

    @property
    @lru_cache()
    def cell(self) -> Cell:
        """The ARD Grid cell of the tile"""
        return Cell(self.quadkey, zone=self.zone)

    @property
    @lru_cache()
    def data_mask(self):
        return loads(self.properties["wkt"])

    @property
    @lru_cache()
    def no_data_mask(self):
        return shape(self.cell).difference(self.data_mask)

    @property
    def thumbnail_url(self) -> str:
        """The URL thumbnail of the tile from the Browse imagery"""

        return ard_url("browse", "preview", self.acq_id, self.cell_id)

    @property
    @lru_cache()
    def __geo_interface__(self) -> dict:
        return mapping(self.data_mask)

    def __repr__(self) -> str:
        return f"<SelectTile of {self.acq_id} at {self.cell_id}>"


class SelectResult(BaseCollection):
    """The results of a Select or MetaSelect operation.

    This object is converted from the GeoJSON FeatureCollections
    returned by Selects and MetaSelects into Python objects"""

    def __init__(self):
        super().__init__()

    @classmethod
    def from_geojson(cls, geojson):
        self = cls()
        for feature in geojson["features"]:
            if "best_matches" in feature["properties"]:
                for match in feature["properties"]["best_matches"]:
                    self.add_tile(SelectTile(match))
            else:
                try:
                    self.add_tile(SelectTile(feature["properties"]))
                except (KeyError, TypeError):
                    pass
        return self

    def __repr__(self) -> str:
        return (
            f"<SelectResult ({len(self.tiles)} tiles in {len(self.acquisitions)} acquisitions) >"
        )


def ard_bbox_generator(input):
    """
    Takes a Shapely shape object and makes it into a valid intersect geometry for a Select based on a bounding box of the input object
    Args:
        input: a Shapely shape object (can be Point, MultiPoint, LineString, MultiLineString, Polygon, or MultiPolygon)
    Returns:
        Shapely polygon (rectangle) that is large enough to be a valid intersect geometry for a Select
    """

    # we set DEG_KM to 0.01 because at the equator 0.01° = 1.11 km for latitude or longitude and the API wants an area of at least 1 km^2
    # we want the latitude diff to be at least 0.01 but the longitude diff / cos(latitude diff) should equal at least 0.01
    DEG_KM = 0.01
    min_area = DEG_KM * DEG_KM

    try:  # make sure we have a valid Shape
        input.centroid
    except AttributeError:
        raise TypeError(
            "Input type must be a Shapely Point, MultiPoint, LineString, MultiLineString, Polygon, or MultiPolygon"
        )

    # make a bounding box for our input
    bbox = input.envelope

    xmin, ymin, xmax, ymax = bbox.bounds
    xdiff = xmax - xmin
    ydiff = ymax - ymin

    cosy = cos(radians(ymax))

    if bbox.area * cos(radians(ymax)) >= min_area:
        # if area of bbox is large enough, then go ahead and return it
        return bbox

    elif xdiff == 0 and ydiff == 0:
        # we have a point, so increase x and y in equal measure

        extra_x = (DEG_KM / cosy) * 0.5
        extra_y = DEG_KM * 0.5

        xmin -= extra_x
        xmax += extra_x

        ymin -= extra_y
        ymax += extra_y

    elif xdiff >= ydiff:
        # increase y-dimension
        ydim = min_area / (xdiff * cosy)
        extra_y = ydim / 2
        ymin -= extra_y
        ymax += extra_y

    else:  # ydiff > xdiff
        # increase x-dimension
        xdim = min_area / ydiff
        extra_x = xdim / 2
        xmin -= extra_x
        xmax += extra_x

    return box(xmin, ymin, xmax, ymax)
