import json

import click
from maxar_ard_grid import Cell, covers


@click.group()
def cell():
    """Subcommand for ARD Grid cell tools"""

    pass


@click.command()
@click.argument("quadkey", required=True)
@click.argument("zone", required=False)
@click.option("--format", help="Output the cell in different formats: `geojson` for GeoJSON")
def describe(quadkey, zone, format):
    """Output a description of a cell given a QUADKEY and optionally a ZONE

    QUADKEY by itself must be a full Cell ID: z15-230232110
    or
    QUADKEY is just the quadkey: 230232110 plus a ZONE : 15"""

    if zone is None:
        cell = Cell(quadkey)
    else:
        cell = Cell(quadkey, zone=zone)
    # error handling
    if format is None:
        click.secho(f"Cell {cell.quadkey} in zone {cell.zone}", fg="cyan")
        xmin, ymin, xmax, ymax = cell.bounds
        click.secho("UTM bounds: ", fg="cyan")
        click.secho(f" Lower left corner: {xmin}, {ymin}", fg="cyan")
        click.secho(f" Upper right corner: {xmax}, {ymax}", fg="cyan")
        click.secho("Geographic bounds:", fg="cyan")
        xmin, ymin, xmax, ymax = cell.geom_WGS84.bounds
        click.secho(f" Lower left corner: {xmin}, {ymin}", fg="cyan")
        click.secho(f" Upper right corner: {xmax}, {ymax}", fg="cyan")

        click.secho(f"Cell size: {xmax - xmin}m", fg="cyan")
    if format == "geojson":
        click.secho(cell.to_GeoJSON(), fg="cyan")


@click.command(name="covers")
@click.argument("geom", type=str)
@click.option("--zoom", type=int, help="Zoom of cells to calculate, default is 12")
@click.option("--format", help="Output the cellis in different formats: `geojson` for GeoJSON")
def _covers(geom, format, zoom):
    """Calculate the cell IDs that cover a given geometry GEOM. GEOM can be WKT or GeoJSON"""

    if zoom is None:
        cells = covers(geom)
    else:
        cells = covers(geom, zoom=zoom)
    if format is None:
        for cell in cells:
            click.secho(cell.id, fg="cyan")
    if format == "geojson":
        fc = {"type": "FeatureCollection", "features": []}
        for cell in cells:
            fc["features"].append(cell.to_feature())
        click.secho(json.dumps(fc), fg="cyan")


cell.add_command(_covers)
cell.add_command(describe)
