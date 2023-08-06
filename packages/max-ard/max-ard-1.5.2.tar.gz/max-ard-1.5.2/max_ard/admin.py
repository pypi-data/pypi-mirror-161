"""Perform admin functions

Provides
--------
  Administrative functions

  - Check data usage at the user or account level
  - add/delete/get/list stored user credentials

"""
import base64
import urllib

from datetime import datetime
from functools import wraps
from posixpath import join
from typing import Union

from pydantic import BaseModel

from max_ard.base_collections import hydrate, UsageArea, UsageCost, UsageLimits, UsageAvailable
from max_ard.exceptions import MissingARDResource
from max_ard.monitor import Monitor
from max_ard.session import ard_url, get_self, get_user_session, paginated_response


__all__ = ["AccountManager"]


class AdminUsage(BaseModel):
    """A model to hold account or user usage"""

    area: UsageArea
    cost: UsageCost
    limits: UsageLimits
    available: UsageAvailable

    def __str__(self):
        def u(val):
            if val == -1:
                return "unlimited"
            else:
                return f"{val:.2f}"

        return f"""
 Data Usage
 ----------

  Account limit: {u(self.limits.limit_sqkm)} sq.km (${u(self.limits.annual_subscription_fee_limit)})

  Imagery ordered: {self.area.total_imagery_sqkm} sq.km (${self.cost.total_imagery_cost})
  ├ Fresh (< 90 days): {self.area.fresh_imagery_sqkm} sq.km (${self.cost.fresh_imagery_cost})
  ├ Standard (90 days - 3 years): {self.area.standard_imagery_sqkm} sq.km (${self.cost.standard_imagery_cost})
  └ Training (> 3 years): {self.area.training_imagery_sqkm} sq.km (${self.cost.training_imagery_cost})

  Remaining balance: {u(self.available.available_sqkm)} sq.km (${u(self.available.total_imagery_balance)})
  
  """


class RegisteredCredentials(BaseModel):
    "A model to hold stored user credentials"
    credentials_id: str
    account_id: str
    description: Union[str, None]
    created: str
    modified: str

    def __repr__(self):
        return f'<RegisteredCredentials "{self.credentials_id}" ({self.short_description})>'

    @property
    def short_description(self):
        if len(self.description) > 20:
            return self.description[0:20] + "..."
        else:
            return self.description


class AccountManager:
    """Manages account-related actions

    Arguments
    ---------
    account_id : str (optional)
        Account ID to manage. If not provided, will use the current user's account
    session : Requests session object (optional)
        The session to use to communicate with the API. If not provided, uses the current user's authenticated session
    """

    __all__ = ["get_account_usage", "get_user_usage"]

    def __init__(self, account_id=None, session=None) -> None:
        if not session:
            session = get_user_session()
        self.session = session
        if not account_id:
            account_id = get_self(self.session)["user"]["account_id"]
        self.account_id = account_id

    def admin_url(self, *args):
        return ard_url("admin", "account", self.account_id, *args)

    @property
    def properties(self):
        return self.session.get(self.admin_url()).json()["account"]

    ########
    # Usage
    ########

    def _validate_dates(self, *args):
        """Validate that dates are YYYY-MM-DD

        Arguments
        ---------
        *args : str
            One or more date strings to validate

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If one or more dates was not YYYY-MM-DD"""

        for date in args:
            if date not in [None, ""]:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Dates must be YYYY-MM-DD")

    def get_account_usage(self, start_date=None, end_date=None):
        """Get account-level data usage

        Parameters
        ----------
        start_date : str (optional)
            Start date to calculate usage
        start_date : str (optional)
            End date to calculate usage

        Returns
        -------
        AdminUsage
            Object model of data usage
        """

        url = ard_url("usage", "account", self.account_id)

        self._validate_dates(start_date, end_date)

        params = {"start_date": start_date, "end_date": end_date}

        r = self.session.get(url, params=params)
        return AdminUsage(**r.json()["usage"])

    def get_user_usage(self, username=None, start_date=None, end_date=None):
        """Get user-level data usage

        Parameters
        ----------
        username : str (optional)
            User name to calculate usage for, if not provided the current user is used
        start_date : str (optional)
            Start date to calculate usage
        end_date : str (optional)
            End date to calculate usage

        Returns
        -------
        AdminUsage
            Object model of data usage
        """

        if not username:
            username = get_self(self.session)["user"]["user_id"]

        url = ard_url("usage", "user", username)

        self._validate_dates(start_date, end_date)

        params = {"start_date": start_date, "end_date": end_date}

        r = self.session.get(url, params=params)
        return AdminUsage(**r.json()["usage"])

    #####
    # Credentials Storage
    #####

    def add_credentials(self, name, credentials, description=None):
        """Saves credentials in the Crendentials API

        The stored credentials key (SAS Url for Azure or Base64-encoded Credentials JSON for GCS) is never returned.
        Only the name, description, and other metadata about the credentials object is provided.

        This is only available to Admin users. However all users in the account may use a stored credential name
        to provide write access when ordering data.

        Parameters
        ----------
        name : str
            Name of the stored credentials, should have URL-friendly characters (no spaces)
        credentials : str
            Credentials secret to store (SAS Url for Azure or Base64 Credentials JSON for GCS).
            If this is a path to a GCS JSON file, it will be read and Base64 encoded.
        description : str (optional)
            Description of the credentials

        Returns
        -------
        dict
            API response JSON dictionary
        """

        if urllib.parse.quote(name) != name:
            raise ValueError(
                "Stored credential names should not use characters that require URL-encoding"
            )
        url = self.admin_url("credentials", "name")

        try:
            with open(credentials, "rb") as binary_file:
                encoded = base64.b64encode(binary_file.read())
                credentials = encoded.decode("ascii")

        except (FileNotFoundError, OSError):
            pass

        payload = {"credentials": credentials, "description": description}
        response = self.session.put(url, json=payload)

        if response.status_code == 204:
            return None
        else:
            return response.json()

    def get_credentials(self, name, raw=False):
        """Retrieves information about stored credentials.

        The stored credentials key (SAS Url for Azure or Crendentials JSON for GCS) is never returned,
        only the name, description, and other metadata about the credentials object.

        This is only available to Admin users. However all users in the account may use a stored credential name
        to provide write access when ordering data.

        Parameters
        ----------
        name : str
            Name of the stored credentials
        raw : bool (optional)
            Return the response JSON

        Returns
        -------
        RegisteredCredentials
            Object model of credentials
        """

        url = self.admin_url("credentials", "name")
        response = self.session.get(url)
        if raw:
            return response.json()
        else:
            return RegisteredCredentials(**response.json()["registered_credentials"])

    def list_credentials(self, raw=False):
        """Retrieves all stored credentials in an account.

        The stored credentials key (SAS Url for Azure or Crendentials JSON for GCS) is never returned,
        only the name, description, and other metadata about the credentials object.

        This is only available to Admin users. However all users in the account may use a stored credential name
        to provide write access when ordering data.

        Parameters
        ----------
        raw : bool (optional)
            Return the response JSON

        Returns
        -------
        List of RegisteredCredentials
            List of object models of credentials
        """

        # responses can be paginated
        id_key = lambda credential: credential["registered_credentials"]["credentials_id"]
        url = self.admin_url("credentials")

        credentials = paginated_response(self.session, url, id_key)

        if raw:
            return credentials
        else:
            object_key = lambda credential: credential["registered_credentials"]
            return hydrate(RegisteredCredentials, credentials, key=object_key)

    def delete_credentials(self, name):
        """Deletes stored credentials by name.

        This is only available to Admin users. However all users in the account may use a stored credential name
        to provide write access when ordering data.

        Parameters
        ----------
        name : str
            Name of the credential object

        """
        url = self.admin_url("credentials", "name")
        return self.session.delete(url)

    #####
    # Monitors
    #####

    def list_monitors(self, raw=False):
        """Retrieves all monitors for an account.

        Parameters
        ----------
        raw : bool (optional)
            Return the response JSON

        Returns
        -------
        List of Monitors
            List of object models of monitors
        """

        id_key = lambda monitor: monitor["monitor_id"]

        url = self.admin_url("monitor")
        monitors = paginated_response(self.session, url, id_key)

        if raw:
            return monitors
        else:
            return [Monitor.from_response(monitor) for monitor in monitors]
