"""Helpers for optional dependencies and platform quirks
"""
import os
import platform

# Conda on Windows proj data
if platform.system() == "Windows":
    # turn on CDN backup files
    os.environ["PROJ_NETWORK"] = "ON"
    # set to Conda's share location
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        os.environ["PROJ_LIB"] = os.path.join(conda_prefix, "Library", "share", "proj")


# Optional dependencies
try:
    import rasterio

    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    import fiona

    HAS_FIONA = True
except ImportError:
    HAS_FIONA = False
