"""Convert ARD Selects to a Shapefile"""

__all__ = ("ShpDoc",)

import json

from shapely.geometry import Polygon, mapping

from max_ard.dependency_support import HAS_FIONA
from max_ard.exceptions import MissingDependency

if HAS_FIONA:
    import fiona
    from fiona.crs import from_epsg


def ShpDoc(geojson, path):
    """Convert a Select represented as a geojson to a shapefile and save

    Parameters
    ----------
    geojson: geojson representing a Select
    path: location to save the shapefile

    Returns
    -------
    none"""
    if not HAS_FIONA:
        raise MissingDependency("Shapefile export requires Fiona")

    dict = json.loads(geojson)

    props = {
        "cell_id": "str",
        "available_tiles": "int",
        "stack_depth_fulfilled": "bool",
        "acquisition_datetime_min": "str",
        "acquisition_datetime_max": "str",
        "best_matches": "str",
    }

    schema = {
        "geometry": "Polygon",
        "properties": props,
    }

    # Write a new shapefile
    with fiona.open(path, "w", crs=from_epsg(4326), driver="ESRI Shapefile", schema=schema) as shp:

        for feat in dict["features"]:

            tuple_coords = [tuple(coords) for coords in feat["geometry"]["coordinates"][0]]
            polygon = Polygon(tuple_coords)
            p = feat["properties"]
            best_matches = p["best_matches"]

            best_str = ""
            for i in range(len(best_matches)):
                best_str += str(best_matches[i])
                if i < len(best_matches) - 1:
                    best_str += ", "

            p["best_matches"] = best_str

            shp.write({"geometry": mapping(polygon), "properties": p})
