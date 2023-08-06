""" Convert ARDCollections to QGIS Layer format"""

import warnings

warnings.warn(
    "max_ard.outputs.qlr_format.QlrDoc has been moved to max_ard.io.QlrDoc",
    DeprecationWarning,
    stacklevel=2,
)

from max_ard.io import QlrDoc as NewQlrDoc


def QlrDoc(collection, public=False):
    """Return a an ARDCollection as a QGIS layer file

    Parameters
    ----------
    collection : ARDCollection
    public : bool, optional
      True if the data is in a public S3 bucket location (see Notes)

    Returns
    -------
    str
      QLR document contents of the ARDCollection

    Notes
    -----
    Passing `public=true` will convert s3:// URLs to the public http:// S3 endpoints.
    This functionality does not work yet for other storage types. It's functionality
    is primarily for creating QLRs of the official Maxar ARD sample datasets at
    http://maxar-ard-samples.s3-website-us-east-1.amazonaws.com/
    """

    warnings.warn(
        "max_ard.outputs.qlr_format.QlrDoc has been moved to max_ard.io.QlrDoc",
        DeprecationWarning,
        stacklevel=2,
    )
    return NewQlrDoc(collection, public)
