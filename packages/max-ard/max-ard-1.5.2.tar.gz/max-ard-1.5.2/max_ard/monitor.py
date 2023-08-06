""" ARD Monitors

ARD Monitors watch AOIs and send notifications when new imagery is acquired. Monitors 
can be created with queries to restrict which acquisitions trigger a notification.

Provides
--------

- Create, retrieve, list, and delete monitors

Notes
-----

Monitors currently support the following notification types:
- Email
- Amazon SNS

Examples
-------

Create a monitor that will watch a bounding box for new imagery collected
by Worldview 1 and send an email when new acquisitions are available:

>>> from max_ard import Monitor

>>> bbox = [-120.1, 43.6, -120.7, 44.2]

>>> query = query = {"platform": {"eq": "worldview-01"}}

>>> monitor = Monitor(bbox=bbox, query=query)

>>> monitor.add_email_notification("me@example.com")

>>> monitor.submit()
"""

import warnings
from typing import List, Union, Any

from maxar_ard_grid import Cell
from max_ard.base_collections import (
    ARDModel,
    Submitted,
    hydrate_with_responses,
    EmailNotification,
    SNSNotification,
)
from max_ard.exceptions import MissingARDResource, NotSubmitted
from max_ard.session import ard_url, get_user_session, link_paginated_response
from max_ard.io import convert_to_shapely
from pydantic import BaseModel
from shapely.geometry import mapping, MultiPolygon


class MonitorAction(BaseModel):
    """Model for monitoring actions

    Note: The only action so far is "notify"
    """

    action: str
    notifications: List[Union[EmailNotification, SNSNotification]] = []


class MonitorRequest(ARDModel):
    """Model of Monitor API Request to send"""

    name: str = None
    description: str = None
    # filter
    intersects: str = None
    bbox: List = None
    # destination
    query: dict = None
    actions: List[MonitorAction] = []

    class Config:
        extra = "allow"
        validate_assignment = True


class MonitorResponse(BaseModel):
    """Model of Monitor API Response"""

    cell_ids: List[str]
    monitor_id: str
    account_id: str
    user_id: str
    name: str = None
    description: str = None
    active: bool
    intersects: Union[str, dict] = None
    bbox: List = None
    query: dict = {}
    actions: List[dict]
    created: str

    class Config:
        extra = "allow"
        validate_assignment = True


class Monitor(Submitted):
    """Object for creating and retrieving ARD Monitors

    Parameters
    ----------
    intersects : Geometry-like objects, str (optional))
        Geometry to intersect, can be most geometry or spatial objects, or a path (see Notes)
    bbox : interable of numeric
        Bounding box in WGS84 coordinates, [west, south, east, north]
    name : str
        Optional name for the monitor (display only)
    description : str
        Optional description for the monitor (display only)
    query : dict
        Query dictionary
    session : session object, optional
        A user_session or application_session object


    Notes
    -----

    Intersects inputs:
        Geometry objects: Shapely shapes, objects supporting __geo_interface__, geojson-like dicts,
            geojson and wkt strings
        Geometry iterables: iterables of above, Fiona readers
        File paths: most spatial file formats. WKT and Geojson supported with base install, other formats
            require Fiona for reading
    """

    def __init__(
        self, intersects=None, bbox=None, name=None, description=None, query={}, session=None
    ):

        self.session = session or get_user_session()
        if intersects is not None:
            intersects = convert_to_shapely(intersects).wkt
        self.request = MonitorRequest(
            name=name, description=description, intersects=intersects, bbox=bbox, query=query
        )
        self.response = None

    def add_email_notification(self, address: str) -> None:
        """Add an email notification to the Monitor

        Parameters
        ----------
        address : str
            Email address to receive order notifications

        Returns
        -------
        None
        """

        notification = EmailNotification(address=address)
        self.request.actions.append(MonitorAction(action="notify", notifications=[notification]))

    def add_sns_notification(self, topic_arn: str) -> None:
        """Add an AWS SNS notification topic to receive Monitor notifications

        Parameters
        ----------
        topic_arn : str
            AWS SNS topic ARN to recieve order notifications

        Returns
        -------
        None
        """

        notification = SNSNotification(topic_arn=topic_arn)
        self.request.actions.append(MonitorAction(action="notify", notifications=[notification]))

    @property
    def submitted(self) -> bool:
        """Submittal state of the monitor"""
        if self.response is None:
            return False
        else:
            return self.response.monitor_id is not None

    @Submitted.required
    def get_history(self) -> List[dict]:
        """Get the history of image matches for this monitor

        Parameters
        ----------
        None

        Returns
        -------
        list
            List of match data dictionaries

        Notes
        -----
        This is not intended to be polled for matches - you can use Select or the Metadata API to check
        for new results.
        """

        url = ard_url("monitor", "history", self.monitor_id)
        id_key = lambda monitor: monitor["monitor_id"]
        monitors = link_paginated_response(self.session, url, id_key)

        return monitors  # ?

    @classmethod
    def list_monitors(
        cls, session=None, raw: bool = False, **kwargs
    ) -> List[Union[dict, "Monitor"]]:
        """List monitors

        Parameters
        ----------
        session: Session
            A user_session or application_session objectj, default uses current user
        raw: bool
            Returns dictionaries if True, Default is to return Monitor objects

        Keywords
        --------
        kwargs
            Pass-through HTTP parameters

        active_only: bool, default is True
            Only show active monitors

        Returns
        -------
        list of dict or Monitor
            Monitors
        """

        url = ard_url("monitor")
        session = session or get_user_session()
        try:
            responses = link_paginated_response(session, url, **kwargs)
        except MissingARDResource:
            return []

        if raw:
            return responses
        else:
            return hydrate_with_responses(Monitor, MonitorResponse, responses, session=session)

    @property
    @Submitted.required
    def monitor_id(self) -> str:
        """Monitor ID"""
        return self.response.monitor_id

    @property
    @Submitted.required
    def cells(self) -> List[Cell]:
        """List of cells being watched by the monitor, as maxar_ard_grid Cell objects"""
        return [Cell(cell) for cell in self.response.cell_ids]

    @property
    def notifications(self) -> List[Union[EmailNotification, SNSNotification]]:
        "List of notifications for this monitor"
        return [action["notification"] for action in self.actions if action["action"] == "notify"]

    def __getattr__(self, name: str) -> Any:
        if self.submitted:
            return getattr(self.response, name)
        try:
            return getattr(self.request, name)
        except AttributeError as e:
            if name not in MonitorResponse.__fields__.keys():
                raise e

        raise NotSubmitted(f"Can't access `{name}` until Monitor has been submitted")

    @classmethod
    def from_id(cls, monitor_id: str) -> "Monitor":
        """Retrieve a Monitor by its ID

        Parameters
        ----------
        monitor_id: str
            Monitor ID

        Returns
        -------
        Monitor
            Requested Monitor

        Raises
        ------
        MissingARDResource
            The ID can not be found.
        """
        response_obj = cls.get_monitor(monitor_id)["monitor"]
        return cls.from_response(response_obj)

    @classmethod
    def from_response(cls, response: dict) -> "Monitor":
        """Create a Monitor object using an API response dictionary of attributes

        Parameters
        ----------
        response: dict
            Monitor attribute dict

        Returns
        -------
        Monitor

        """
        instance = cls()
        instance.response = MonitorResponse(**response)
        return instance

    @staticmethod
    def get_monitor(monitor_id: str, session=None) -> dict:
        """Retrieve a Monitor API payload by its ID

        Parameters
        ----------
        monitor_id: str
            Monitor ID
        session: Session
            A user_session or application_session objectj, default uses current user

        Returns
        -------
        dict
            Requested monitor API payload

        Raises
        ------
        MissingARDResource
            The ID can not be found.
        """
        session = session or get_user_session()
        url = ard_url("monitor", "config", monitor_id)
        return session.get(url).json()

    @staticmethod
    def send_monitor(payload: dict, session=None) -> dict:
        """Post a Monitor API payload

        Parameters
        ----------
        payload: dict
            API monitor payload
        session: Session
            A user_session or application_session objectj, default uses current user

        Returns
        -------
        dict
            Created monitor API payload
        """

        session = session or get_user_session()
        url = ard_url("monitor")

        return session.post(url, json=payload).json()

    def submit(self) -> None:
        """Submit this monitor to the API"""

        if self.submitted:
            warnings.warn("This select has already been submitted")
            return

        payload = self.request.to_payload()
        response = self.send_monitor(payload, session=self.session)
        self.response = MonitorResponse(**response["monitor"])

    @Submitted.required
    def delete(self) -> None:
        """Soft delete this monitor from the API.

        This sets the monitor's `active` flag to `False`. Inactive monitors are not returned
        by the list endpoint unless the parameter `active_only=False` is sent.

        An inactive monitor does not run but still can be fetched by its ID.

        """
        url = ard_url("monitor", "config", self.monitor_id)
        self.session.delete(url)

    def __repr__(self) -> str:
        if self.submitted:
            monitor_id = self.monitor_id
        else:
            monitor_id = "(unsubmitted)"
        if self.name is None:
            name = ""
        else:
            name = f": '{self.name}'"
        return f"<Monitor {monitor_id}{name}>"

    @property
    def __geo_interface__(self):
        """Python Geospatial Interface"""
        geoms = [cell.geom_WGS84 for cell in self.cells]
        return mapping(MultiPolygon(geoms))
