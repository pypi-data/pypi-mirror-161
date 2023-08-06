"""Search ARD tile metadata

Provides
--------
  1. A MetaSelect class for Select-like searches performed at the metadata level
  2. Functions for tile metadata searches
  3. An implementation of a multithreaded batch search function
  4. Functions for tile summary metadata searches.


Documentation
-------------

Coming soon

Examples
-------

Using a search function that returns GeoJSON FeatureCollection formatted data

    >>> from max_ard.metadata import search_by_area, MetaSelect
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

    >>> tiles = search_by_area(datetime=datetime, bbox=bbox, query=query, stack_depth=3)
    >>> tiles['features'][0]

Using a MetaSelect for a similar interface to Select objects

    >>> select = MetaSelect(datetime=datetime, bbox=bbox, query=query, stack_depth=3)
    >>> results = s.results
    >>> print(results)
    < SelectResult (95 tiles in 12 acquisitions) >
    >>> results.dates
    ['2020-07-10',
    '2020-07-24',
    '2020-07-29',
    '2020-09-08',
    '2020-10-21',
    '2021-01-16']
 
Get summary metadata for a tile

    >>> summarize_cell(id, id)

"""


from concurrent.futures import as_completed
from copy import deepcopy
from typing import List, Union, Any

from requests_futures.sessions import FuturesSession
from shapely.geometry import box
from shapely.ops import unary_union
from shapely.prepared import prep

from max_ard.io import convert_to_shapely
from max_ard.select import SelectResult
from max_ard.session import get_user_session, ard_url
from max_ard.exceptions import (
    ARDServerException,
    MissingSummary,
    MissingARDResource,
    GeometryException,
)
from maxar_ard_grid import covers


###
# MetaSelect Objects
###


class MetaSelect:
    """An ARD API MetaData Select object

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
        Maximum number of tiles to return, default is all tiles
    image_age_category : iterable of str, optional
        One or
    session : session object, optional
        A user_session or application_session object

    Attributes
    ----------

    results: Results
        A container object holding ARDtile objects

    Notes
    -----

    The `MetaSelect` object works like a standard `Select` object but uses the SDK's batch select functionality to retrieve results faster. Since `MetaSelects` break up the search work and do not generate output files, they generally will generate results over large areas that can cause a regular Select to fail.

    There are a few differences in how `MetaSelects` work:

    - Default stack depth is unlimited, use `stack_depth` to set a limit on tiles returned.
    - There is no scoring on query parameters. Instead tiles are returned sorted newest to oldest. A `stack_depth` of 5 will return the five most recent matching tiles. If `stack_depth` is not provided, all results will be returned.
    - The search is run when the object is initialized. You do not need to call `submit()` or `wait_for_success()`, however for compatibility both methods can be called without raising errors. The same applies to properties like `succeeded` - they are set to the appropriate values for compatibility but if the object successfully initializes, it has already completed the search process.
    - Usage data is not calculated.
    - No file artifacts are generated, so the following methods and attributes will raise NotImplemented errors:

    - select_id
    - from_id()
    - get_select()
    - usage
    - get_signed_link()
    - get_link_contents()
    - copy_link()

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading"""

    def __init__(
        self,
        acq_ids: List[str] = None,
        datetime: str = None,
        intersects=None,
        bbox: list = None,
        query: dict = {},
        stack_depth: int = None,
        image_age_category: List[str] = None,
        session=None,
    ):

        kwargs = {
            "filters": [],
            "session": session,
            "acq_ids": acq_ids,
            "datetime": datetime,
            "intersects": intersects,
            "bbox": bbox,
            "query": query,
            "stack_depth": stack_depth,
            "image_age_category": image_age_category,
            "session": session,
        }

        tiles = batch_search_by_area(**kwargs)
        self.results = SelectResult.from_geojson(tiles)
        self.succeeded = True
        self.failed = False
        self.running = False
        self.finished = True
        self.status = "SUCCEEDED"
        self.state = "SUCCEEDED"

    def submit() -> None:
        pass

    def wait_for_success(self, interval: int = 5) -> None:
        pass

    not_implemented = {
        "select_id": "MetaSelects use batch search and do not have an ID",
        "from_id": "MetaSelects use batch search and do not have an ID",
        "get_select": "MetaSelects use batch search and do not have an ID",
        "usage": "For faster response time, MetaSelects do not calculate usage",
        "get_signed_link": "MetaSelects do not generate files, see .results()",
        "get_link_contents": "MetaSelects do not generate files, see .results()",
        "copy_link": "MetaSelects do not generate files, see .results()",
    }

    def __getattr__(self, val):
        if val in self.not_implemented:
            raise NotImplemented(self.not_implemented[val])

    def __repr__(self) -> str:
        return f"<ARD MetaSelect>"


###
# Cell Metadata
###


def search_by_cell_id(
    cell_id: str,
    acq_ids: List[str] = [],
    datetime: str = None,
    intersects=None,
    bbox: list = None,
    query: dict = {},
    stack_depth: int = None,
    image_age_category: List[str] = [],
    format: str = "geojson",
    session=None,
) -> dict:

    """Searches for tile metadata within a given ARD grid cell.

    Parameters
    ----------
    cell_id : str
        An ARD tile cell ID, like Z10-302310230201
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
        Maximum number of tiles to return, default is to return all tiles
    image_age_category : iterable of str, optional
        One or
    session : session object, optional
        A user_session or application_session object
    format: str
        either 'geojson' (default), 'order', or 'stac'

    Returns
    -------
    dict
        output dictionary, see Notes

    Notes
    -----
    Default stack depth is unlimited, use `stack_depth` to set a limit on tiles returned. There is no scoring on parameters, so if results are limited by passing a stack depth, tiles are returned sorted newest to oldest. A `stack_depth` of 5 will return the five most recent tiles.

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading

    Formats:
        "geojson": GeoJSON FeatureCollection format, each tile is a Feature
        "order": A dictionary used by the order system: keys are acquisition IDs, values are lists of cell IDs
        "stac": STAC search API collection format"""

    url = ard_url("metadata", "cells", cell_id, f"acquisitions?format={format}")

    if intersects is not None:
        intersects = convert_to_shapely(intersects).wkt

    payload = {
        "ids": acq_ids,
        "datetime": datetime,
        "intersects": intersects,
        "bbox": bbox,
        "stack_depth": stack_depth,
        "query": query,
        "image_age_category": image_age_category,
    }
    payload = {k: v for k, v in payload.items() if v not in [None, [], ()]}

    session = session or get_user_session()
    return session.post(url, json=payload).json()


def search_by_area(
    acq_ids: List[str] = [],
    datetime: str = None,
    intersects=None,
    bbox: list = None,
    query: dict = {},
    stack_depth: int = None,
    image_age_category: List[str] = [],
    format: str = "geojson",
    session=None,
) -> dict:
    """Searches for tile metadata within a given area.

    Parameters
    ----------
    acq_ids : iterable of str
        An iterable of acquisition IDs to search for
    datetime : str
        Date or date range string
    intersects : Geometry-like objects, str
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
    format: str
        either 'geojson' (default), 'order', or 'stac'

    Returns
    -------
    dict
        output dictionary, see Notes

    Notes
    -----
    Default stack depth is unlimited, use `stack_depth` to set a limit on tiles returned. There is no scoring on parameters, so if results are limited by passing a stack depth, tiles are returned sorted newest to oldest.

    A geometry is required (either `intersects` or `bbox`) if acquisition IDs are not passed. If IDs are passed without a geometry, it is assumed all tiles from those acquisitions should be returned.

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading

    Formats:
        "geojson": GeoJSON FeatureCollection format, each tile is a Feature
        "order": A dictionary used by the order system: keys are acquisition IDs, values are lists of cell IDs
        "stac": STAC search API collection format"""

    url = ard_url("metadata", "cells", f"acquisitions?format={format}")

    if intersects is not None:
        intersects = convert_to_shapely(intersects).wkt

    payload = {
        "ids": acq_ids,
        "datetime": datetime,
        "intersects": intersects,
        "bbox": bbox,
        "stack_depth": stack_depth,
        "query": query,
        "image_age_category": image_age_category,
    }
    payload = {k: v for k, v in payload.items() if v not in [None, [], ()]}

    session = session or get_user_session()
    return session.post(url, json=payload).json()


def batch_search_by_area(filters: list = [], session=None, **kwargs) -> dict:
    """A multithreaded batch search for tile metadata over a given area.

    - the search area is broken down to individual tiles
    - the tiles are searched asychronously in 8 parallel threads
    - custom filter functions can be run on each batch in the asychronous process
    - only returns the GeoJSON format

    Parameters
    ----------
    filters : list of functions
        A list of functions to use to filter tiles (see Notes)
    acq_ids : iterable of str
        An iterable of acquisition IDs to search for
    datetime : str
        Date or date range string
    intersects : Geometry-like objects
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric
        Bounding box in WGS84 coordinates, [west, south, east, north] if `intersects` is not provided
    query : dict
        Query dictionary
    stack_depth: int or None, optional
        Maximum number of tiles to return, default is all tiles
    image_age_category : iterable of str, optional
        One or more of "training", "standard", "fresh"
    session : session object, optional
        A user_session or application_session object


    Returns
    -------
    dict
        GeoJSON FeatureCollection format, each tile is a Feature dictionary.

    Notes
    -----
    Stack depth:
        Default stack depth is unlimited, use `stack_depth` to set a limit on tiles returned.
        Tiles are scored only on recency and you will receive the most recent matching tiles
        up to your stack depth.

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading

    Filter functions:
        These should take the GeoJSON Feature formatted tile dictionary as an input, and return True
        if the tile meets the filter requirements. For example:

            def match_worldview(tile):
                # check if the word "world" is in the platform name
                return "world" in tile["properties"]["platform"].lower()

        A tile must pass all filters to be returned (they are logically ANDed). Filters execute in order,
        so more expensive filters can be placed later in the list.

    """

    # get the AOI
    if "bbox" in kwargs:
        if kwargs["bbox"] is not None:
            aoi = box(*kwargs["bbox"])
        del kwargs["bbox"]
    if "intersects" in kwargs:
        if kwargs["intersects"] is not None:
            aoi = convert_to_shapely(kwargs["intersects"])
        del kwargs["intersects"]

    prep_aoi = prep(aoi)
    fetches = []
    for cell in covers(aoi):
        url = ard_url("metadata", "cells", cell.id, "acquisitions?format=geojson")
        payload = kwargs.copy()
        payload = {k: v for k, v in payload.items() if v not in [None, [], ()]}
        intersection = aoi.intersection(cell.geom_WGS84)
        # skip intersections that are touching but don't have an area
        if not intersection.is_empty:
            # interior cells that are covered don't need an AOI
            if not prep_aoi.contains_properly(intersection):
                # since the intersection can be less than the 1 sqkm limit, send the full geometry
                payload["intersects"] = aoi.wkt
            fetches.append((url, payload))

    def filter_hook(response, *args, **kwargs):
        tiles = response.json()["features"]
        if len(filters) > 0:
            filter_fn = lambda tile: all([fn(tile) for fn in filters])
            response.tiles = filter(filter_fn, tiles)
        else:
            response.tiles = tiles

    session = session or get_user_session()

    tiles = []

    # requests-futures lets you "add" hooks as a kwarg
    # but these clobber existing hooks
    # so we'll add the filter hook to the hooks and then reset them back
    old_hooks = deepcopy(session.hooks)
    session.hooks["response"].append(filter_hook)
    try:
        with FuturesSession(session=session) as future_session:
            futures = [future_session.post(url, json=payload) for url, payload in fetches]
            for future in as_completed(futures):
                try:
                    tiles.extend(future.result().tiles)
                # tiles that are overlapped by an area too small to order are skipped
                except GeometryException as g:
                    raise g
    except Exception as e:
        raise e
    finally:
        session.hooks = old_hooks
    return {"type": "FeatureCollection", "features": tiles}


def get_acquisition(
    acq_id: str,
    format: str = "geojson",
    session=None,
) -> dict:
    """Get all ARD metadata for an acquisition

    Parameters
    ----------
    acq_id : str
        Acquisition ID for the tile
    session : session object, optional
        A user_session or application_session object
    format: str
        either 'geojson' (default), 'order', or 'stac'

    Returns
    -------
    dict
        output dictionary, see Notes

    Notes
    -----
    Formats:
        "geojson": GeoJSON FeatureCollection format, each tile is a Feature
        "order": A dictionary used by the order system: keys are acquisition IDs, values are lists of cell IDs
        "stac": STAC search API collection format"""

    return search_by_area(acq_ids=[acq_id], format=format, session=session)


def get_tile(
    cell_id: str,
    acq_id: str,
    session=None,
) -> dict:

    """Get a specific ARD tile's metadata

    Parameters
    ----------

    cell_id : str
        ARD grid cell ID for the tile
    acq_id : str
        Acquisition ID for the tile
    session : session object, optional
        A user_session or application_session object

    Returns
    -------
    dict
        GeoJSON Feature format of the ARD tile
    """

    url = ard_url("metadata", "cells", cell_id, "acquisitions", acq_id)

    session = session or get_user_session()
    return session.get(url).json()


####
# Summary Service
####


def summarize_cell(cell_id: str, session=None) -> dict:
    """Get a specific ARD cell's summary metadata

    Parameters
    ----------
    cell_id : str
        ARD grid cell ID
    session : session object, optional
        A user_session or application_session object

    Returns
    -------
    dict
        Summary metadata

    Raises
    ------
    MissingSummary
        The cell is not in an area indexed by the summary service.
        Any area can be added to the summary service using `register_summary_area()`
    """

    url = ard_url("metadata", "cells", cell_id, "summary")

    session = session or get_user_session()
    try:
        response = session.get(url)
    except MissingARDResource:
        msg = (
            f"Cell {cell_id} is not being indexed by the metadata summary service. \n"
            + "Use register_summary_coverage(geometry) to index this area and try again."
        )
        raise MissingSummary(msg)
    return response.json()


def summarize_area(intersects=None, bbox: list = None, strict: bool = False, session=None) -> dict:
    """Get a ARD cell summary metadata over an area

    Parameters
    ----------
    intersects : Geometry-like objects
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric
        Bounding box in WGS84 coordinates, [west, south, east, north] if `intersects` is not provided
    strict : bool, default is False
        Use strict mode. In strict mode missing summary tiles will raise MissingSummary exceptions
    session : session object, optional
        A user_session or application_session object

    Returns
    -------
    dict
        Summary metadata

    Raises
    ------
    MissingSummary
        If `strict=True`, some portion of the input area is not indexed by the summary service.
        Any area can be added to the index service by using `register_summary_area()`

    Notes
    -----
    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading
    """
    url = ard_url("metadata", "cells", "summary")

    payload = {}
    if bbox is not None:
        payload["bbox"] = bbox
    if intersects is not None:
        intersects = convert_to_shapely(intersects).wkt
        payload["intersects"] = intersects

    session = session or get_user_session()
    results = session.post(url, json=payload).json()
    if strict:
        intersects = intersects or box(*bbox)
        coverage = list(covers(intersects))
        if len(coverage) != len(results["features"]):
            raise MissingSummary(
                "The area requested does not have full coverage of summary data. \n"
                + "Register your area using register_summary_area() and try again."
            )
    return results


def register_summary_area(intersects=None, bbox: List = None, session=None) -> dict:
    """Register an area to be indexed by the summary service

    Parameters
    ----------
    intersects : Geometry-like objects
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric
        Bounding box in WGS84 coordinates, [west, south, east, north] if `intersects` is not provided
    session : session object, optional
        A user_session or application_session object

    Notes
    -----
    The summary service was initally indexing major metropolitan areas. You can add any additional areas you require.
    Summary areas do not need to be managed or deleted. Resubmitting an area or overlapping a previous one does not cause
    duplication.

    Intersects inputs:
        Geometry objects: Shapely shapes, GeoJSON-like dicts, GeoJSON and wkt strings,
            objects supporting __geo_interface__ like maxar_ard_grid.Cell
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading
    """
    url = ard_url("metadata", "cells", "summary", "register")

    payload = {}
    if bbox is not None:
        payload["bbox"] = bbox
    if intersects is not None:
        intersects = convert_to_shapely(intersects).wkt
        payload["intersects"] = intersects

    session = session or get_user_session()
    return session.post(url, json=payload).json()
