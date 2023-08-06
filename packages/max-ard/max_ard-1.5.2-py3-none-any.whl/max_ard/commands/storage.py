import json
import os
import sys

import boto3
import botocore
import click

from max_ard.ard_collection import ARDCollection
from max_ard.exceptions import BucketInitError, BucketRevokeError
from max_ard.io import QlrDoc
from max_ard.storage import init_bucket, revoke_bucket


@click.group()
def storage():
    """Commands related to ARD data storage"""
    pass


@click.command()
@click.argument("location")
@click.option("--profile", help="Use this AWS profile for access")
def init(location, profile=None):
    """Creates an S3 bucket if LOCATION does not exist, then authorizes the ARD data writer by adding a PutObject statement to the bucket policy of LOCATION"""
    try:
        init_bucket(location, profile=profile)
    except Exception as e:
        click.secho(f"There was a problem initializing the bucket: {str(e)}", err=True, fg="red")


@click.command()
@click.argument("location")
@click.option("--profile", help="Use this AWS profile for access")
def revoke(location, profile=None):
    """Removes the bucket policy statement from LOCATION, preventing the ARD writer from writing to the bucket"""
    try:
        revoke_bucket(location, profile=profile)
    except Exception as e:
        click.secho(
            f"There was a problem revoking access to the bucket: {str(e)}", err=True, fg="red"
        )


@click.command()
@click.argument("location")
@click.option("--dest", help='Output filename, "<filename>.qlr" for QGIS Layer Definition')
@click.option("--format", help='Format to send to stdout, "qlr" for QGIS Layer Definition')
@click.option("--aoi", help="WKT geometry to filter tiles to")
@click.option(
    "--acq_id",
    "acq_id_in",
    multiple=True,
    help="Limit result to this Acquisition ID (can use more than once",
)
@click.option(
    "--zone",
    "zone_in",
    multiple=True,
    help="Limit tiles to those in this zone. Can be used multiple times. This option can speed up scan time of large collections.",
)
@click.option("--earliest_date", help="Return results from on or after this date (YYYY-MM-DD)")
@click.option("--latest_date", help="Return results from this date or earlier (YYYY-MM-DD")
@click.option("--profile", help="Use this AWS profile for access")
@click.option(
    "--public", "anon", is_flag=True, help="Access a public bucket without using credentials"
)
def describe(**kwargs):
    """Gives a summary of ARD tiles in LOCATION (S3 or local path)"""

    format = kwargs.pop("format", None)
    dest = kwargs.pop("dest", None)
    location = kwargs.pop("location", None)
    c = ARDCollection(location, **kwargs)

    # pluralizer
    def s(i):
        s = "s"
        try:
            i = len(i)
        except:
            pass
        if i == 1:
            s = ""
        return s

    if format is None and dest is None:

        click.secho(f"Examining ARD data in {location}...", fg="cyan")
        # this will trigger access, see if it fails
        try:
            count = len(c.acq_ids)
        except PermissionError:
            click.secho(
                f"Your credentials for accessing {location} are invalid or expired",
                err=True,
                fg="red",
            )
            raise click.Abort()
        if count == 0:
            click.secho("No ARD tiles found", fg="red")
            raise click.Abort()
        click.secho(f"{count} acquisition{s(count)}", fg="cyan")
        click.secho(f"{len(c.tiles)} tile{s(c.tiles)}", fg="cyan")
        click.secho(f"Earliest date: {c.start_date}", fg="cyan")
        click.secho(f"Latest date: {c.end_date}", fg="cyan")
        zones = ",".join([str(z) for z in c.zones])
        click.secho(f"UTM zone{s(c.zones)}: {zones}", fg="cyan")
    elif format == "qlr" and dest is None:
        click.secho(QlrDoc(c, kwargs["anon"]), fg="cyan")
    elif dest.lower().endswith(".qlr"):
        with open(dest, "w") as out:
            out.write(QlrDoc(c, kwargs["anon"]))
    else:
        click.secho(
            "QGIS Layer (--format qlr or --dest filename.qlr) is the only current export type",
            fg="red",
        )


storage.add_command(init)
storage.add_command(revoke)
storage.add_command(describe)
