import json
import logging
import os
from json.decoder import JSONDecodeError

from shapely import wkt
from shapely.errors import WKTReadingError
from shapely.geometry import GeometryCollection, shape
from shapely.geometry.base import BaseGeometry

from max_ard.dependency_support import HAS_FIONA
from max_ard.exceptions import MissingDependency, UnknownFileType

from maxar_ard_grid import Cell

if HAS_FIONA:
    import fiona
    from fiona.collection import Collection as FionaCollection


def convert_to_shapely(input):
    """Convert input geometry or geometry filepath to Shapely shape object

    Args:
        input: a geometry object with one or more features, or filepath to such a geometry object, as:
            - a dict that follows the Python Geometry Interface (GeoJSON-like)
            - a GeoJSON feature-like dict that has a 'geometry' key
            - a Fiona dataset reader
            - a Shapely shape *or iterable of Shapely shapes* (in which case the input will be returned as is)
            - strings in WKT, GeoJSON, or GeoJSON geometry
            - maxar_ard_grid Cells

    Returns:
        Shapely shape object of input (or iterable of Shapely shapes, if that was the input)

    * Note: if the input has multiple features, the output will be a GeometryCollection *
    """

    # ignore Nones, empty strings, other falsey things

    if not input:
        return input

    # check if we already have a Shapely shape
    if isinstance(input, BaseGeometry):
        return input

    # for Cells we need to return the WGS84 representation
    # since they are natively in UTM
    if isinstance(input, Cell):
        return input.geom_WGS84

    # or an iterable of Shapely shapes
    try:
        if all([isinstance(item, BaseGeometry) for item in input]):
            return input
    except TypeError:
        pass

    # GeoJSON-like (__geo_interface__) -- single feature
    try:
        return shape(input)
    except:
        pass

    try:
        return shape(input["geometry"])
    except:
        pass

    # GeoJSON feature collection
    try:
        return GeometryCollection([shape(g["geometry"]) for g in input["features"]])
    except:
        pass

    def fiona_converter(reader):
        geom = list(reader)
        if len(geom) > 1:
            return GeometryCollection([shape(g["geometry"]) for g in geom])
        else:
            return shape(geom[0]["geometry"])

    if HAS_FIONA and type(input) == FionaCollection:
        try:
            return fiona_converter(input)
        except:
            pass

    if type(input) is not str:
        raise TypeError("Invalid object - check list of acceptable types.")

    def quiet_wkt_loads(input):
        logger = logging.getLogger("shapely.geos")
        old_level = logger.level
        logger.setLevel(logging.CRITICAL)
        try:
            geom = wkt.loads(input)
        except Exception as e:
            raise (e)
        finally:
            logger.setLevel(old_level)
        return geom

    # strings could be wkt, json, or a path to a vector file
    if os.path.exists(input):
        try:
            return quiet_wkt_loads(open(input, "r").read())
        # try to read filepath with Fiona
        except (WKTReadingError, UnicodeDecodeError):
            if not HAS_FIONA:
                raise MissingDependency("Fiona is needed to read vector formats")
            try:
                reader = fiona.open(input)
                return fiona_converter(reader)
            except:
                raise UnknownFileType(
                    "Could not open the contents of the given file, is it a valid file?"
                )

    else:

        # wkt string
        try:
            return quiet_wkt_loads(input)
        except WKTReadingError:
            pass

        # json string, convert to dict and start over
        try:
            return convert_to_shapely(json.loads(input))
        except JSONDecodeError:
            pass

        raise TypeError("String input does not match WKT or JSON, or a valid file path")
