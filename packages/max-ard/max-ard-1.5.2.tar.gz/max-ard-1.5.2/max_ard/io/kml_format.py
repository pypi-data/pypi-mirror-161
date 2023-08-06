"""Convert ARD Selects to a KML File"""

import os

from shapely.geometry import shape
from shapely.geometry.polygon import orient

from max_ard.session import ard_url

__all__ = ("KmlDoc",)


def KmlDoc(select):
    """Convert a Select to a KML file

    Parameters
    ----------
    select: Select

    Returns
    -------
    str
        A KML document of the Select"""

    results = select.results
    folders = []
    acquisitions = results.acquisitions
    acquisitions.sort(key=lambda x: x.date)
    folders = (KmlFolder(acquisition) for acquisition in acquisitions)
    folders = "\n".join(folders)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
        <Document id="1"> 
            <Style id="red">
                <LineStyle>
                    <color>ff0000ff</color>
                    <colorMode>normal</colorMode>
                </LineStyle>
                <PolyStyle>
                    <colorMode>normal</colorMode>
                    <fill>0</fill>
                    <outline>1</outline>
                </PolyStyle>
            </Style>
            {folders}
        </Document>
    </kml>"""


def KmlFolder(acquisition):

    tiles = (TileLayer(tile) for tile in acquisition)
    tiles = "\n".join(tiles)

    return f"""
        <Folder>
        <name>{acquisition.acq_id}</name>
        {tiles}
    </Folder> """


def TileLayer(tile):

    return f"""
    {KmlPolygon(tile)}
    {KmlOverlay(tile)}"""


def KmlPolygon(tile):

    # make sure the geometry is CCW wound
    geom = orient(shape(tile))
    coords = [(*t, 0) for t in geom.exterior.coords]
    coords = " ".join([f"{c[0]},{c[1]},{c[2]}" for c in coords])

    return f"""
        <Placemark>
        <name>{tile.cell.id}</name>
        <styleUrl>#red</styleUrl>
        <Polygon>
            <outerBoundaryIs>
                <LinearRing>
                    <coordinates>{coords}</coordinates>
                </LinearRing>
            </outerBoundaryIs>
        </Polygon>
    </Placemark>"""


def KmlOverlay(tile):

    # browse isn't part of the ard api, don't use ard_url()
    url = ard_url("browse", "preview", tile.acq_id, tile.cell_id)
    overlay_geom = orient(shape(tile.cell.geom_WGS84))
    quad_pts = list(overlay_geom.exterior.coords)[:4]
    # these need to go ll, lr, ur, rl pairs
    # so we rotate until ll is at the front of the quad
    cx, cy = overlay_geom.centroid.coords[0]
    from shapely.geometry import box

    while quad_pts[0][0] >= cx or quad_pts[0][1] >= cy:
        quad_pts.append(quad_pts.pop(0))
    quad_pts = [(*t, 0) for t in quad_pts]
    coords = " ".join([f"{c[0]},{c[1]},{c[2]}" for c in quad_pts])

    return f"""
        <GroundOverlay>
        <name>{tile.acq_id}</name>
        <Icon>
            <href>{url}</href>
        </Icon>
        <gx:LatLonQuad>
            <coordinates>{coords}</coordinates>
        </gx:LatLonQuad>
    </GroundOverlay>"""
