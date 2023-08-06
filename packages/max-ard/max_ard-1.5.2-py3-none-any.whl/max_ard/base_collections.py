"""Base collection types for ARD

Provides
--------
- Pydantic Models that are used in multiple places
- Submitted and Succeeded ABCs that add "requires" decorators
- Collections of tiles
- Collections of tiles from a common acquisition
- Collections of tiles covering a common grid cells

These collection objects assume a generic concept of a "tile". They can be used to
group tiles-to-be found in a Select, or real tiles delivered to a storage location.
"""
from abc import ABC, abstractmethod
from functools import wraps
from tempfile import NamedTemporaryFile
from typing import List, Union

from maxar_ard_grid.grid import Cell
from pydantic import BaseModel
from shapely.geometry import MultiPolygon, mapping

from max_ard.dependency_support import HAS_RASTERIO
from max_ard.exceptions import NotSuccessful, NotFinished, NotSubmitted, SelectError
from max_ard.processing import AcquisitionReader

if HAS_RASTERIO:
    import rasterio


def hydrate(cls, things, key=None):
    """Convenience function for hydrating objects from a list of dicts

    Arguments
    ---------
    cls: Object class to create
    things: iterable of raw object dicts
    key: like in sort(), function that exposes where in the dict the object's arguments are

    Returns
    -------
    list
        list of objects of type cls

    Notes
    -----
    If a key function is not provided, the dict is assumed to hold the object arguments.
    Operator.itemgetter(<name>) or a lamba x: x[<name>] can be used.

    """
    if key is None:
        key = lambda x: x
    return [cls(**key(thing)) for thing in things]


def hydrate_with_responses(cls, response_cls, responses, **kwargs):
    instances = []
    for response in responses:
        instance = cls(**kwargs)
        instance.response = response_cls(**response)
        instances.append(instance)

    return instances


###
# Common Pydantic Models
###


class ARDModel(BaseModel):
    """A Pydantic BaseModel with sanitized dicts

    The ARD API can be picky about Nones and empty objects so for request payloads
    we can use the to_payload method to generate a cleaned up payload"""

    def to_payload(self):
        """sends only parameters with values"""
        params = self.dict().copy()
        payload = {k: v for k, v in params.items() if v not in (None, (), [])}
        return payload


class EmailNotification(BaseModel):
    """A model for Email Notifications"""

    type: str = "email"
    address: str

    class Config:
        allow_mutation: False


class SNSNotification(BaseModel):
    """A model for SNS Notifications"""

    type: str = "sns"
    topic_arn: str

    class Config:
        allow_mutation: False


class UsageArea(BaseModel):
    """A model to hold ARD usage by area"""

    fresh_imagery_sqkm: float
    standard_imagery_sqkm: float
    training_imagery_sqkm: float
    total_imagery_sqkm: float
    estimate: bool


class UsageCost(BaseModel):
    """A model to hold ARD image costs, estimated or consumed

    A value of None for a cost means your account does not have pricing set
    for this category. Without set pricing this category can not be ordered."""

    fresh_imagery_cost: Union[float, None]
    standard_imagery_cost: Union[float, None]
    training_imagery_cost: Union[float, None]
    total_imagery_cost: Union[float, None]
    estimate: bool


class UsageLimits(BaseModel):
    """A model to hold account limits"""

    limit_sqkm: float
    fresh_imagery_fee_limit: float
    standard_imagery_fee_limit: float
    training_imagery_fee_limit: float
    annual_subscription_fee_limit: float


class UsageAvailable(BaseModel):
    """A model to hold account balances

    When returned with a select, these numbers reflect the account balance at the time
    the select was submitted. Usage estimates are not applied to these numbers."""

    available_sqkm: float
    fresh_imagery_balance: float
    standard_imagery_balance: float
    training_imagery_balance: float
    total_imagery_balance: float


###
# Validation ABCs
###


class Submitted(ABC):
    """An ABC for objects that can be submitted

    - Concrete classes that inherit from Submitted must override submitted()
    - `submitted` is usually exposed as a @property
    - how you determine an object has been submitted is up to you

    For methods that require the object to have been submitted, wrap it with
    the @Submitted.required decorator
    """

    @abstractmethod
    def submitted(self):
        pass

    @staticmethod
    def required(func):
        @wraps(func)
        def func_wrapper(instance, *args, **kwargs):
            if not instance.submitted:
                raise NotSubmitted(
                    f"Can't access `{func.__name__}` until {type(instance).__name__} has been submitted"
                )
            res = func(instance, *args, **kwargs)
            return res

        return func_wrapper


class Succeeded(ABC):
    """An ABC for objects that have a succeeded state, and by definition
    must also be submitted in order to run

    - Concrete classes that inherit from Submitted must override
        - submitted()
        - finished()
        - succeeded()
    - see also Submitted

    For methods that require the object to have succeeded, wrap it with
    the @Succeeded.required decorator
    """

    @abstractmethod
    def submitted(self):
        pass

    @abstractmethod
    def finished(self):
        pass

    @abstractmethod
    def succeeded(self):
        pass

    @staticmethod
    def required(func):
        @wraps(func)
        def func_wrapper(instance, *args, **kwargs):
            if not instance.submitted:
                raise NotSubmitted(
                    f"Can't access `{func.__name__}` until {type(instance).__name__} has been submitted"
                )
            if not instance.finished:
                raise NotFinished(
                    f"Can't access `{func.__name__}` until {type(instance).__name__} has finished running"
                )
            if not instance.succeeded:
                # This error should probably be generic, but only Selects use this ABC so far
                if type(instance).__name__ == "Select":
                    raise SelectError(f"Can't access `{func.__name__}` due to an error")
                else:
                    raise NotSuccessful(f"Can't access `{func.__name__}` due to an error")

            res = func(instance, *args, **kwargs)
            return res

        return func_wrapper


###
# Classes for ARD Concepts
###


class Acquisition(list):
    """Container for one or more tiles from a single acquisition

    These are generated by ARDCollections and would not normally be initialized"""

    def __init__(self, acq_id: str, tiles: list = []) -> None:

        self.acq_id = acq_id
        """ str: ID of this acquisition """
        super().__init__(*tiles)

    @property
    def cells(self) -> List[Cell]:
        cells = set([tile.cell for tile in self])
        return list(cells)

    def get_tile_from_cell(self, cell):
        cell = Cell(cell)
        for tile in self:
            if tile.cell == cell:
                return tile
        raise ValueError("Tile not found in this acquisition")

    def __str__(self):
        return f"<Acquisition at {self.acq_id} ({len(self)} tiles)>"

    def __repr__(self):
        tiles = ", ".join([f"<{type(tile).__name__} at {tile.cell.id}>" for tile in self])
        return f"<Acquisition of {self.acq_id} [{tiles}]>"

    def __hash__(self):
        """Hash of cell ID"""
        return hash(self.acq_id)

    def open_acquisition(self):
        """Return a Rasterio reader that accesses all of the Acquisition object's tiles.

        A Rasterio DatasetReader opened on a VRT of all acquisition tiles"""

        return AcquisitionReader(self)

    @property
    def date(self):
        return self[0].date

    @property
    def properties(self) -> dict:
        """Strip level properties"""

        props = self[0].properties
        # todo: check if catalog_id is still passed in metadata
        keep = ["catalog_id", "acquisition_id", "platform", "scan_direction", "epsg", "datetime"]
        strip_props = {}
        for key in keep:
            try:
                strip_props[key] = props[key]
            except KeyError:
                pass
        return strip_props

    @property
    def __geo_interface__(self) -> dict:
        geoms = [tile.cell.geom_WGS84 for tile in self]
        return mapping(MultiPolygon(geoms))


class Stack(list):
    """Container for one or more tiles in an ARD grid cell

    These are generated by ARDCollections and would not normally be initialized"""

    def __init__(self, cell: Cell, tiles: list = []) -> None:

        self.cell = Cell(cell)
        super().__init__(*tiles)

    @property
    def tiles(self):
        """not needed but provides access to tiles for GeoMixin"""
        return self

    def get_tile_from_acquisition(self, acq_id):
        for tile in self:
            if tile.acq_id == acq_id:
                return tile
        raise ValueError("Tile not found in this stack")

    @property
    def acquisition_ids(self) -> List[str]:
        ids = set([tile.acq_id for tile in self])
        return list(ids)

    def __str__(self):
        return f"<Stack at {self.cell.id} ({len(self)} tiles)>"

    def __repr__(self):
        tiles = ", ".join([f"<{type(tile).__name__} of {tile.acq_id}>" for tile in self])
        return f"<Stack at {self.cell.id} [{tiles}]>"

    def __hash__(self):
        """Hash of cell ID"""
        return hash(self.cell)

    @property
    def __geo_interface__(self) -> dict:
        geoms = [tile.cell.geom_WGS84 for tile in self]
        return mapping(MultiPolygon(geoms))


class Store(dict):
    """A defaultdict-like k:v store for objects"""

    def __init__(self, object_type, *args, **kwargs):
        self.object_type = object_type
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        res = self[key] = self.object_type(key)
        return res


class BaseCollection:
    def __init__(self):
        self._reset()

    def _reset(self):
        """Used by ARDCollection when a rescan is triggered"""
        self._acquisitions = Store(Acquisition)
        self._stacks = Store(Stack)
        self._zones = set()
        self._dates = set()

    def add_tile(self, tile):
        self._acquisitions[tile.acq_id].append(tile)
        self._stacks[tile.cell].append(tile)
        self._zones.add(tile.cell.zone)
        self._dates.add(tile.date)

    @property
    def tiles(self):
        """All the ARD Tiles in this collection"""
        return [tile for tiles in self.stacks for tile in tiles]

    def get_tile(self, acq_id, cell):
        """Get a tile from the collection

        Parameters
        ----------
        acq_id : str
            Acquisition ID
        cell : str or maxar_ard_grid.Cell
            Cell of the tile, can be a cell ID or Cell object

        Returns
        -------
        ARDTile or SelectTile
        """
        cell = Cell(cell)
        acq = self.get_acquisition(acq_id)
        for tile in acq:
            if tile.cell == cell:
                return tile
        raise ValueError("Tile not found in this collection")

    @property
    def dates(self) -> List[str]:
        """All of the dates of acquisitions in the ARDCollection"""
        dates = list(self._dates)
        dates.sort()
        return dates

    @property
    def start_date(self) -> str:
        """Earliest date of acquisitions in the ARDCollection as YYYY-MM-DD"""
        return self.dates[0]

    @property
    def end_date(self) -> str:
        # does the type get caught?
        """Latest date of acquisitions in the ARDCollection as YYYY-MM-DD"""
        return self.dates[-1]

    @property
    def zones(self) -> List[int]:
        """The UTM zones covered by tiles in the ARDCollection"""
        return list(self._zones)

    #
    # Stacks
    #

    @property
    def stacks(self):
        """All of ARD grid stacks in the collection"""
        return list(self._stacks.values())

    @property
    def cells(self):
        """All of the ARD grid Cell objects in the collection"""
        return list(self._stacks.keys())

    def get_stack(self, cell):
        """Get a stack of tiles from the collection

        A Stack object is a container of all tiles covering a given ARD grid cell.
        Parameters
        ----------
        cell : str or maxar_ard_grid.Cell
            Cell of the tile, can be a cell ID or Cell object

        Returns
        -------
        Stack
        """
        cell = Cell(cell)
        try:
            return self._stacks[cell]
        except KeyError:
            raise ValueError(f"Stack for cell {cell} not found in this collection")

    #
    # Acquisitions
    #

    @property
    def acquisitions(self):
        """All of the acquisitions present in the collection"""
        return list(self._acquisitions.values())

    @property
    def acquisition_ids(self):
        """All of the acquisitions IDs present in the collection"""
        return list(self._acquisitions.keys())

    @property
    def acq_ids(self):
        """Shorthand name for .acquisition_ids"""
        return self.acquisition_ids

    def get_acquisition(self, acq_id):
        """Get an acquisition from the collection

        An Acquisition object is a container of all tiles from a given acquisition.

        Parameters
        ----------
        acq_id : str
            Acquisition ID

        Returns
        -------
        Acquisition
        """
        try:
            return self._acquisitions[acq_id]
        except KeyError:
            raise ValueError(f"Aquisition for ID {acq_id} not found in this collection")

    @property
    def __geo_interface__(self) -> dict:
        geoms = [tile.cell.geom_WGS84 for tile in self.tiles]
        return mapping(MultiPolygon(geoms))
