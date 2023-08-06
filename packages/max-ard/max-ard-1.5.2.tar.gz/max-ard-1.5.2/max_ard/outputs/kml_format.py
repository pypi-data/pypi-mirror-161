import warnings

warnings.warn(
    "max_ard.outputs.kml_format.KmlDoc has been moved to max_ard.io.KmlDoc", DeprecationWarning
)

from max_ard.io import KmlDoc as NewKmlDoc


def KmlDoc(select):
    """Convert a Select to a KML file

    Parameters
    ----------
    select: Select

    Returns
    -------
    str
        A KML document of the Select"""

    warnings.warn(
        "max_ard.outputs.kml_format.KmlDoc has been moved to max_ard.io.KmlDoc", DeprecationWarning
    )
    return NewKmlDoc(select)
