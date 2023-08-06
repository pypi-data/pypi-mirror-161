"""Export ARD collections to other file formats

Provides
--------
- QGIS Layer export of ARDCollections
- KML, KMZ, SHP exports of Selects

Notes
-----
Selects and ARDCollections export to different formats due to the underlying data formats.

There is not currently a way for Google Earth to read the ARD COGs directly. For KMLs to display 
would require either thumbnails to be produced of the COGs, or some sort of KML SuperOverlay
web service to be set up.

It might be possible to display selects in QGIS, but since the Select browse image preview tiles
do not have georeferencing files it would take some experimentation to correctly configure
their layers, or add the ability to the preview endpoint to answer requests for georeferencing files
"""

from .inputs import convert_to_shapely
from .kml_format import KmlDoc
from .kmz_format import KmzDoc
from .qlr_format import QlrDoc
from .shp_format import ShpDoc
