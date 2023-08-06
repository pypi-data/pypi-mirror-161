import pprint
import re
import sys

import click

from max_ard.ard_collection import ARDCollection
from max_ard.exceptions import ARDServerException, BadARDRequest
from max_ard.io import QlrDoc
from max_ard.order import Order
from max_ard.select import Select


@click.group()
def order():
    """Tools for ordering ARD products"""
    pass


@click.command()
@click.argument("order_id", required=True)
@click.option(
    "--format", help="Output the order status in other formats: `raw` for the full response JSON"
)
def status(order_id, format):
    """Gets the status of an order given the ORDER_ID"""

    try:
        order = Order.from_id(order_id)

    except Exception as e:
        click.secho(str(e), err=True, fg="red")
        sys.exit()
    if format == "raw":
        click.secho(str(order.response.dict()), fg="cyan")
    else:
        click.secho(order.state, fg="green" if order.state == "SUCCEEDED" else "cyan")


@click.command()
@click.argument("order_id", required=True)
@click.option("--format", help='Output the order in other formats: "qlr" for QGIS layer')
@click.option("--verbose", "-v", is_flag=True, help="Return more information about the Order")
def describe(order_id, format, verbose=False):
    """Outputs order details"""
    try:
        order = Order.from_id(order_id)
    except Exception as e:
        click.secho(str(e), err=True, fg="red")
        sys.exit()
    pp = pprint.PrettyPrinter(indent=4)
    if format == "qlr":
        c = ARDCollection.from_order(order)
        click.echo(QlrDoc(c))
        exit()
    if not order.finished:
        click.secho("Order has not finished running", fg="cyan")
        if verbose:
            click.secho("*******************", fg="cyan")
            click.secho("Request details:", fg="cyan")
            click.secho(pp.pformat(order.response.order.dict()), fg="cyan")
        exit()
    c = ARDCollection.from_order(order)
    click.secho(f"getting Order ID {order_id}", fg="green")
    click.secho("*******************", fg="green")
    click.secho("Order details:", fg="green")
    click.secho(pp.pformat(order.response.order.dict()), fg="cyan")
    click.secho("*******************", fg="green")
    if format is None:

        def S(i):
            s = "s"
            try:
                i = len(i)
            except:
                pass
            if i == 1:
                s = ""
            return s

        try:
            count = len(c.acq_ids)
        except PermissionError:
            click.secho(
                f"Your credentials for accessing the order are invalid or expired",
                err=True,
                fg="red",
            )
            exit()
        if count == 0:
            click.secho("No ARD tiles found", fg="red")
            exit()
        click.secho(f"{count} acquisition{S(count)}", fg="green")
        click.secho(f"{len(c.tiles)} tile{S(c.tiles)}", fg="green")
        click.secho(f"Earliest date: {c.start_date}", fg="green")
        click.secho(f"Latest date: {c.end_date}", fg="green")
        zones = ",".join([str(z) for z in c.zones])
        click.secho(f"UTM zone{S(c.zones)}: {zones}", fg="green")
    else:
        click.secho("QGIS Layer (--format qlr) is the only available format", fg="red")
    click.secho("\n\n", fg="cyan")


class NumericType(click.ParamType):
    name = "numeric"

    def convert(self, value, param, ctx):
        try:
            return float(value)
        except TypeError:
            self.fail(
                "expected string for int() conversion, got "
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )
        except ValueError:
            self.fail(f"{value!r} is not a value that can be converted to a float", param, ctx)


NUM_TYPE = NumericType()


@click.command()
@click.option(
    "--destination",
    required=True,
    help="Destination of the tiles: an S3 bucket and optional prefix",
)
@click.option(
    "--select-id",
    help="Order the results of Select with the Select ID, pass LISTEN to find the ID from the piped output of a Select",
)
@click.option("--select_id", help="deprecated to only use dashes in options")
@click.option(
    "--acq-id",
    "acquisitions",
    multiple=True,
    help="Order a given acquisition by acquisition ID, can be provided multiple times."
    + "If provided with a Select ID will only generate tiles for the provided IDs.",
)
@click.option(
    "--acquisition-id", "long_acquisitions", multiple=True, help="deprecated, use --acq_id"
)
@click.option(
    "--acquisition_id",
    "old_acquisitions",
    multiple=True,
    help="deprecated to only use dashes in options",
)
@click.option(
    "--intersects",
    help="Only generate tiles that intersect this geometry in WKT format, or geometry from this file path.",
)
@click.option(
    "--role-arn", help="A trusted Role ARN for the writer to assume so it can write tiles."
)
@click.option("--role_arn", help="deprecated to only use dashes in options")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Submit the order for basic validation without processing the order",
)
@click.option(
    "--bbox",
    nargs=4,
    type=NUM_TYPE,
    help="Like --intersects, but takes a bounding box in the form --bbox XMIN YMIN XMAX YMAX",
)
@click.option(
    "--bba",
    type=bool,
    default=False,
    help="Use Bundle Block Adjustment to align images within this order. See docs for limitations and best practices for using BBA.",
)
@click.option(
    "--add-email",
    "emails",
    multiple=True,
    help="Add an email address to receive order notifications. Can be used multiple times to add more than one email address.",
)
@click.option(
    "--add-sns",
    "topics",
    multiple=True,
    help="Add an AWS SNS topic to send nofications to. Can be used multiple times to add more than one topic.",
)
@click.option("--verbose", "-v", is_flag=True, help="Return more information about the Order")
@click.option("--yes", "-y", is_flag=True, help="Skip order confirmation")
def submit(**kwargs):
    """Submit an ARD Order"""

    # options that don't get sent to the API
    emails = kwargs.pop("emails", [])
    topics = kwargs.pop("topics", [])
    verbose = kwargs.pop("verbose", False)
    confirm_order = not kwargs.pop("yes", False)

    # TODO: clean this up after old args are removed
    # note the API wants the underscore so we will need to map it to the underscored name
    # will do this in Click but for now being explicit is less confusing

    # deprecations warnings to the user
    if kwargs.get("select_id", None) is not None:
        click.secho(
            "Note: `--select_id` will be deprecated, use `--select-id` instead", fg="yellow"
        )

    if kwargs.get("role_arn", None) is not None:
        click.secho(
            "Note: `--role_arn` will be deprecated, use `--role-arn` instead.", fg="yellow"
        )

    if kwargs.get("acquisition_id", None) is not None:
        click.secho(
            "Note: `--acquisition_id` will be deprecated, use `--acq-id` instead.", fg="yellow"
        )

    if kwargs.get("acquisition-id", None) is not None:
        click.secho(
            "Note: `--acquisition-id` will be deprecated, use `--acq-id` instead.", fg="yellow"
        )

    # move select-id to select_id
    select_arg = kwargs.pop("select-id", None)
    if select_arg is not None:
        kwargs["select_id"] = select_arg

    # move role-arn to role_arn
    role_arg = kwargs.pop("role-arn", None)
    if role_arg is not None:
        kwargs["role_arn"] = role_arg

    # gather up any acquisitions
    acquisitions = set()

    for arg in ["acquisitions", "long_acquisitions", "old_acquisitions"]:
        acqs = kwargs.pop(arg, None)
        if acqs is not None:
            for a in acqs:
                acquisitions.add(a)

    kwargs["acquisitions"] = list(acquisitions)

    # Listen for a select ID on stdin

    if kwargs["select_id"] is not None and kwargs["select_id"].lower() == "listen":
        click.secho(f"Listening...", fg="cyan")
        stdin = click.get_text_stream("stdin")
        stderr = click.get_text_stream("stderr")
        if stderr.readable():
            err_msg = stderr.read()
            if len(err_msg.strip()) > 0:
                click.secho(f"Error on stderr: {err_msg}", err=True)
                exit()
        try:
            select_id = re.match(r"Select (\d+)", stdin.read())[1]
            click.secho(f"Input stream matched select {select_id}", fg="cyan")
        except TypeError:
            click.secho(
                f"Input stream was not usable, did the Select succeed?", fg="red", err=True
            )
            exit()
        try:
            select = Select.from_id(select_id)
        except ARDServerException as e:
            msg = "A Select ID was found, but there was an error fetching its details: \n"
            msg += str(e)
            click.secho(msg, fg="red", err=True)
            exit()
        select.wait_for_success()
        kwargs["select_id"] = select_id
        click.secho(f"Ordering from Select {select_id}", fg="cyan")
    try:
        order = Order(**kwargs)
    except Exception as e:
        click.secho(f"There was an error in your parameters: {e}", fg="red", err=True)
        exit()

    if not emails and not topics:
        if confirm_order:
            if input("No notifications supplied, do you still want to order?") != "y":
                exit()
    for email in emails:
        order.add_email_notification(email)
    for topic in topics:
        order.add_sns_notification(topic)

    if verbose:
        pp = pprint.PrettyPrinter(indent=4)
        click.secho(f"Request payload:", fg="cyan")
        click.secho(pp.pformat(order.request.to_payload()), fg="cyan")

    if kwargs["dry_run"]:
        click.secho("Checking order in dry-run mode...", fg="cyan")
        try:
            order.submit()
        except BadARDRequest as e:
            click.secho(f"There was an error in your request: {e}", err=True, fg="red")
            exit()
        click.secho("Dry run successful", fg="green")
    else:
        if confirm_order:
            if input("Are you sure you want to order? (y/n) ") != "y":
                exit()
        try:
            order.submit()
            click.secho(f"Order {order.order_id} has been submitted", fg="cyan")
            click.secho(
                f"Run `max-ard order status {order.order_id}` to check the status", fg="cyan"
            )
            click.secho('When the status is "SUCCEEDED" you can: ', fg="cyan")
            click.secho(
                f"Run `max-ard order describe {order.order_id}` to see a basic overview of the results",
                fg="cyan",
            )
            click.secho("Run `max-ard order` to see all the `order` commands", fg="cyan")
        except BadARDRequest as e:
            click.secho(f"There was an error in your request: {e}", err=True, fg="red")


order.add_command(status)
order.add_command(describe)
order.add_command(submit)
