"""Place ARD Orders

Provides
--------
  1. Place an ARD order
  2. Test an ARD order with "dry-run" mode
  3. Check order status

Reference
---------

Ordering API overview

- https://ard.maxar.com/docs/select-and-order/order-ard/

SDK Ordering Tutorial

- https://ard.maxar.com/docs/sdk/sdk/ordering-ard/

API request and response examples

- https://ard.maxar.com/docs/api-reference/order/order_resource/


Example
-------

>>> from max_ard import Order
>>> order = Order(destination='my_bucket/my_ard_tiles', select_id=<Select ID>)
>>> order.add_email_notification('me@email.com')
>>> order.submit()

"""

import base64
import json
import warnings
from typing import List, Union

from pydantic import BaseModel

from max_ard.base_collections import (
    ARDModel,
    Submitted,
    UsageArea,
    UsageCost,
    EmailNotification,
    SNSNotification,
    hydrate_with_responses,
)
from max_ard.exceptions import ARDServerException, BadARDRequest, NotSubmitted
from max_ard.io import convert_to_shapely
from max_ard.session import ard_url, get_user_session, paginated_response


__all__ = ("Order",)

#######
# Models
#######


class Acquisition(BaseModel):
    id: str
    cells: List[str] = []

    class Config:
        validate_assignment = True


class Output_Config(BaseModel):
    bucket: str
    prefix: str
    role_arn: str = None

    class Config:
        validate_assignment = True


class S3_Config(BaseModel):
    sas_url: str = None
    bucket: str
    prefix: str

    class Config:
        validate_assignment = True
        extra: "forbid"


class GCS_Config(BaseModel):
    service_credentials: str = None
    credentials_id: str = None
    bucket: str
    prefix: str

    class Config:
        validate_assignment = True
        extra: "forbid"


class AZ_Config(BaseModel):
    sas_url: str = None
    credentials_id: str = None
    container: str
    prefix: str

    class Config:
        validate_assignment = True
        extra: "forbid"


class OrderRequest(ARDModel):
    acquisitions: List[Acquisition] = None
    select_id: str = None
    dry_run: bool = False
    # filter
    intersects: str = None
    bbox: List = None
    # destination
    output_config: dict = None
    settings: dict = {}
    notifications: List[Union[EmailNotification, SNSNotification]] = []
    metadata: dict = {}

    class Config:
        extra = "allow"
        validate_assignment = True


class OrderUsage(BaseModel):
    area: UsageArea = None
    cost: UsageCost = None


class OrderDetails(BaseModel):
    usage: OrderUsage = None

    class Config:
        extra = "allow"


class OrderResponse(BaseModel):
    id: str
    status: str
    status_message: str = None
    order: OrderDetails = None

    class Config:
        extra = "allow"
        validate_assignment = True


#####
# Classes
#####


class Order(Submitted):
    """An ARD API Order object

    Parameters
    ----------
    acquisitions : iterable of str or dict, optional
        An iterable of acquisitions to order, see Notes
    select_id : str
        A Select ID to order, see Notes
    destination:
        For S3 locations only, a path to storage location such as s3://my-bucket/my-prefix
    output_config:
        If not using `destination`, an output configuration dictionary, see API documentation for examples
    intersects : Geometry-like objects, str (optional))
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric, optional
        Like `intersects`, a bounding box in WGS84 coordinates, [XMIN YMIN XMAX YMAX]
    role_arn : str, optional
        A trusted Role ARN for the writer to assume so it can write tiles.
        This is not used if the s3 bucket policy allows writing tiles to the bucket.
    dry_run : bool, optional
        When true, runs pre-order checks to check if order is valid but does not generate imagery
    bba : bool, optional
        When true, Block Bundle Adjustment will be applied to the order.
    metadata : dict, optional
        User-supplied metadata
    settings : dict, optional
        Dictionary of settings to override outputs, see Notes
    session : session object, optional
        A user_session or application_session object

    Attributes
    ----------
    session : session object or None
        A user_session or application_session object
    dry_run : bool
        as above
    submitted : bool
        True if Select has been submitted via `max_ard.order.Order.submit`
    request : Pydantic model
        Parameters are loaded into a Pydantic model of the HTTP API request
    response : Pydantic model
        Pydantic model of the server response to API call. Status and submit calls
        return the same payload.

    Notes
    -----
    An order must specify `acquisitions` or `select_id`.

    If ordering by select ID, do not include acquisition IDs or an AOI in the order request.

    Acquisitions can be a list of acqusitions IDs, or a a list of dictionaries, with the keys
    `id` and `cells`. If no cells are specified, it is assumed all cells are wanted
    (subject to clipping by an AOI or BBOX):


      acquisitions=["103001009E8G3C90"]

      or

      acquisitions=[
        {
            "id": "103001007B478000",
            "cells": ["Z17-031313123113", "Z17-031313123112"]
        },
        {
            "id": "103001009E8C7C00",
            "cells": ["Z17-031313123113"]
        },
        {
            "id": "103001009E8G3C90"
        }
     ]

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading



    Settings dictionary defaults:
        You can override one or more of the following values:

        {
            "bundle_adjust": false,
            "cloud_mask": true,
            "data_mask": true,
            "healthy_vegetation_mask": true,
            "ms_analytic": true,
            "ms_saturation_mask": true,
            "pan_analytic": true,
            "pan_flare_mask": true,
            "terrain_shadow_mask": true,
            "visual": true,
            "water_mask": true
        }"""

    def __init__(
        self,
        acquisitions=None,
        select_id=None,
        destination=None,
        output_config=None,
        settings={},
        intersects=None,
        bbox=None,
        role_arn=None,
        dry_run=False,
        bba=False,
        metadata={},
        session=None,
    ):

        self.session = session or get_user_session()

        # check booleans aren't strings
        if type(dry_run) is not bool:
            raise ValueError(f"Parameter `dry_run` needs to be a boolean, not {type(dry_run)}")
        if type(bba) is not bool:
            raise ValueError(f"Parameter `bba` needs to be a boolean, not {type(bba)}")

        # bba to be moved to `settings` instead of top level param
        if "bundle_adjust" not in settings:
            settings["bundle_adjust"] = bba

        # set up the output config
        if destination is not None:
            destination = destination.replace("s3://", "")
            parts = destination.split("/", 1)
            bucket = parts[0]
            try:
                prefix = parts[1]
            except IndexError:
                prefix = ""
            # old style output config
            destination = {"bucket": bucket, "prefix": prefix, "role_arn": role_arn}
            output_config = self._validate_output({"destination": destination})

        else:
            if output_config is not None:
                output_config = self._validate_output(output_config)

        # set up acquisitions
        if type(acquisitions) == str:
            acquisitions = [Acquisition(id=acquisitions)]
        elif type(acquisitions) == list or type(acquisitions) == tuple:
            if len(acquisitions) > 0:
                if type(acquisitions[0]) == str:
                    acquisitions = [Acquisition(id=v) for v in acquisitions]
        elif type(acquisitions) == dict:
            acquisitions = [Acquisition(id=k, cells=v) for k, v in acquisitions.items()]

        # if the intersects is a Shapely geom, convert it to wkt
        if intersects is not None:
            intersects = convert_to_shapely(intersects).wkt

        self.request = OrderRequest(
            acquisitions=acquisitions,
            select_id=select_id,
            intersects=intersects,
            bbox=bbox,
            output_config=output_config,
            settings=settings,
            dry_run=dry_run,
            metadata=metadata,
        )
        self.dry_run = dry_run
        self.response = None

    def _validate_output(self, output_config):

        platforms = {
            "azure_blob_storage": AZ_Config,
            "google_cloud_storage": GCS_Config,
            "amazon_s3": S3_Config,
            "destination": Output_Config,
        }
        platform = list(output_config.keys())[0]
        config_model = platforms.get(platform, None)
        if config_model is None:
            raise ValueError(
                "Output config format not recognized, please see documentation for examples"
            )
        params = output_config[platform].copy()
        # validation on object creation
        config_obj = config_model(**params)

        params = {k: v for k, v in config_obj.dict().items() if v is not None}

        # convert credential files to b64 encoding
        if platform == "google_cloud_storage":
            if "credentials_id" not in params:
                location = params["service_credentials"]

                try:
                    with open(location, "rb") as binary_file:
                        encoded = base64.b64encode(binary_file.read())
                        params["service_credentials"] = encoded.decode("ascii")
                except (FileNotFoundError, OSError):
                    try:
                        creds = base64.b64decode(location)
                        assert "type" in json.loads(creds)
                    except:
                        raise ValueError(
                            "GCS service credentials should be either a Base64-encoded string"
                            + " of the JSON credentials file contents or a path to the JSON credentials file"
                        )
            else:
                if "service_credentials" in params:
                    c_id = params["credentials_id"]
                    warnings.warn(
                        "Both a stored credential ID and service credential argument were provided. "
                        + f'The store credential ID "{c_id}" will be used'
                    )
                    del params["service_credentials"]

        if platform != "destination":
            return {platform: params}
        else:
            return params

    def add_email_notification(self, address):
        """Add an email notification to the order

        Parameters
        ----------
        address : str
            Email address to receive order notifications"""
        self.request.notifications.append(EmailNotification(address=address))

    def add_sns_notification(self, topic_arn):
        """Add an AWS SNS notification topic to receive order notifications

        Parameters
        ----------
        topic_arn : str
            AWS SNS topic ARN to recieve order notifications"""
        self.request.notifications.append(SNSNotification(topic_arn=topic_arn))

    def __repr__(self):
        try:
            return f"<Order {self.order_id} ({self.status})>"
        except NotSubmitted:
            return "<Order (Not submitted)>"

    @property
    def submitted(self):
        if self.response:
            return self.response.id is not None
        else:
            return False

    @property
    @Submitted.required
    def finished(self):
        """The Order finished processing but may have failed"""

        return self.status != "RUNNING"

    @property
    @Submitted.required
    def running(self):
        """The Order is running"""

        return self.status == "RUNNING"

    @property
    @Submitted.required
    def succeeded(self):
        """The Order has finished running and has succeeded"""

        return self.status == "SUCCEEDED"

    @property
    @Submitted.required
    def usage(self):
        if self.response.order is None:
            # just submitted, refresh the order status
            response = self.get_order(self.order_id)
            self.response = OrderResponse(**response)
        return self.response.order.usage

    @property
    @Submitted.required
    def failed(self):
        """The Order has finished running but failed"""

        return self.status in ["FAILED", "ERROR"]

    @property
    @Submitted.required
    def order_id(self):
        """The Order ID"""

        return self.response.id

    @property
    @Submitted.required
    def status(self):
        """State of the order process: 'RUNNING', 'SUCCEEDED, or 'FAILED'"""

        if self.response.status == "RUNNING":
            response = self.get_order(self.order_id)
            self.response = OrderResponse(**response)
        return self.response.status

    @property
    def state(self):
        """Legacy version of `status`, will be deprecated in the future"""
        return self.status

    @classmethod
    def from_id(cls, order_id, session=None):
        """Create a Order object from an ID

        Parameters
        ----------
        order_id: str
            Order ID to hydrate into a Order object
        session : Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        Order"""

        response = cls.get_order(order_id, session)
        instance = cls()
        instance.response = OrderResponse(**response)
        return instance

    @classmethod
    def list_orders(
        cls,
        limit=10,
        starting_after="",
        ending_before="",
        start_date="",
        end_date="",
        filter=None,
        session=None,
    ):
        """Fetch user's orders

        Parameters
        ----------
        limit: int, default 10
            maximum number of orders to fetch
        starting_after: str
            the order_id after which further responses will be returned, paging forward
        ending_before: str
            the order_id before which further responses will be returned, paging backwards
        start_date: str
            starting date to filter, ISO-8601 YYYY-MM-DD
        start_date: str
            ending date to filter, ISO-8601 YYYY-MM-DD
        filter: str
            filter results that match values contained in the given key separated by a colon.
            Example: 'metadata.downstream_customer_id:abdc-534-b4dc47'
        session: Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        list
            Order objects matching parameters"""

        session = session or get_user_session()

        params = {
            "limit": limit,
            "starting_after": starting_after,
            "ending_before": ending_before,
            "start_date": start_date,
            "end_date": end_date,
        }

        if filter is not None:
            params["filter"] = filter

        key = lambda order: order["id"]
        responses = paginated_response(session, ard_url("order"), key, **params)

        return hydrate_with_responses(Order, OrderResponse, responses, session=session)

    @classmethod
    def get_order(cls, order_id, session=None):
        """Fetch raw data about an Order from an ID

        Parameters
        ----------
        order_id : str
            Order ID to fetch metadata for
        session: Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        dict
            API data for the given Order"""

        if not session:
            session = get_user_session()

        r = session.get(ard_url("order", "status", order_id))
        return r.json()

    @classmethod
    def send_order(cls, payload, session=None):
        """Send a request to the Order API

        Parameters
        ----------
        payload : dict
            Order API request payload
        session : Session object, optional
            Authenticated session, such as from get_client_session()

        Returns
        -------
        dict
            API response data for the given Order"""

        if not session:
            session = get_user_session()
        r = session.post(ard_url("order"), json=payload)
        return r.json()

    def submit(self):
        """Submit this Order to the API"""

        response = self.send_order(self.request.to_payload(), session=self.session)
        if self.submitted:
            warnings.warn("The Order has already been submitted")
            return
        if self.dry_run:
            self.response = OrderResponse(
                id="dry run",
                status="SUCCEEDED",
                order={"usage": response["usage"]},
                status_message="Order dry-run validation successful.",
            )
        else:
            self.response = OrderResponse(
                id=response["id"], status="RUNNING", status_message="Order submitted and running."
            )
