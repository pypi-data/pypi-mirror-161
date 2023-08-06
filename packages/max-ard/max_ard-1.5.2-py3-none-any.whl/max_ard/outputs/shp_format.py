"""Convert ARD Selects to a Shapefile"""

import warnings

from max_ard.io import ShpDoc as NewShpDoc


def ShpDoc(geojson, path):
    """Convert a Select represented as a geojson to a shapefile and save

    Parameters
    ----------
    geojson: geojson representing a Select
    path: location to save the shapefile

    Returns
    -------
    none"""

    warnings.warn(
        "max_ard.outputs.shp_format.ShpDoc has been moved to max_ard.io.ShpDoc",
        DeprecationWarning,
        stacklevel=2,
    )
    return NewShpDoc(geojson, path)
