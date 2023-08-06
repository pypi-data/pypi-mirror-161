"""Convert ARD Selects to a KMZ File"""

import warnings

warnings.warn(
    "max_ard.outputs.kmz_format.KmzDoc has been moved to max_ard.io.KmzDoc",
    DeprecationWarning,
    stacklevel=2,
)

from max_ard.io import KmzDoc as NewKmzDoc


def KmzDoc(select, path):
    """Convert a Select to a KMZ file and save

    Parameters
    ----------
    select: Select
    path: path at which to save the KMZ

    Returns
    -------
    none"""

    warnings.warn(
        "max_ard.outputs.kmz_format.KmzDoc has been moved to max_ard.io.KmzDoc",
        DeprecationWarning,
        stacklevel=2,
    )
    return NewKmzDoc(select, path)
