""" Authenticated sessions for communicating with the ARD API endpoints"""

import json
import os
import warnings
from configparser import ConfigParser
from platform import python_version, system

import jwt
from jwt.api_jwt import DecodeError
from oauthlib.oauth2 import BackendApplicationClient, LegacyApplicationClient
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests_oauthlib import OAuth2Session


from max_ard.exceptions import (
    ard_server_request_hook,
    bad_ard_request_hook,
    bad_geom_request_hook,
    oversize_request_hook,
    unauth_request_hook,
    missing_resource_hook,
)

try:
    from importlib import metadata
except ImportError:  # for Python<3.8
    import importlib_metadata as metadata

__all__ = ("get_user_session", "get_client_session", "get_self")

SAVE_TOKEN = True  # if false, never save the token back to the config file
ARD_TIMEOUT = os.environ.get(
    "ARD_TIMEOUT", 30
)  # seconds, this is high for big selects and dry run orders


# Timeout and Retry handling
# from https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTP Adapter that adds in default timeouts

    Keywords
    --------
    timeout(numeric): seconds to wait before timing out

    """

    def __init__(self, *args, **kwargs):
        self.timeout = ARD_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def mount_adaptors(session):
    """Mount adaptors to a session for retries and update UA string

    Arguments
    ---------
    session: Requests session
    """

    retries = Retry(total=3, backoff_factor=5, status_forcelist=[429, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries))
    version = metadata.version("max_ard")
    session.headers.update(
        {"User-Agent": f"max_ard/{version} (Python {python_version()}/{system()})"}
    )
    return session


def link_paginated_response(session, url, **params):
    """Follow responses with paginated links and gather up objects

    Newer paginated endpoints give you a link to retrieve the next set of objects.
    For older endpoints that only return object IDs, see the next function.

    Parameters
    ----------
    session: Requests session
        A session through which to make the requests, usually an ARD session
    url: str
        URL to start fetching objects
    **params: any
        Additional parameters to pass through to the session's GET method

    Returns
    -------
    list: any
        A list of objects returned by the endpoint"""

    response = {"has_more": True}
    things = []
    while response["has_more"]:
        response = session.get(url, params=params).json()
        for thing in response["data"]:
            things.append(thing)
        # nothing returned
        if len(things) == 0:
            return []
        if response["has_more"]:
            url = response["links"]["next_page"]

    return things


def paginated_response(session, url, key, **params):
    """Follow paginated responses with object IDs and gather up objects

    This uses `starting_after` to grab the next batch of objects after the last
    object's ID.

    Parameters
    ----------
    session: Requests session
        A session through which to make the requests, usually an ARD session
    url: str
        URL to start fetching objects
    key: callable
        A callable that given the object, returns the object's ID.
    **params: any
        Additional parameters to pass through to the session's GET method

    Returns
    -------
    list: any
        A list of objects returned by the endpoint"""

    response = {"has_more": True}
    things = []
    while response["has_more"]:
        response = session.get(url, params=params).json()
        for thing in response["data"]:
            things.append(thing)
            last_id = key(thing)
        # nothing returned
        if len(things) == 0:
            return []
        params["starting_after"] = last_id

    return things


def ard_url(*args):
    """Get an ARD url built from given subfolders

    This will build the url using hostname and dev feature branch envvars, if present.

    Parameters
    ----------
    *args: any
        ARD API endpoint subfolders to concatenate into a url

    Returns
    -------
    str: endpoint url

    Examples
    --------

    No hostname or branch set returns prod urls:

        ard_url('select', 'status') -> https://ard.maxar.com/api/v1/select/status

    Hostname set:

        MAXAR_ARD_HOSTNAME = ard-dev.maxar.com

        ard_url('select', 'status') -> https://ard-dev.maxar.com/api/v1/select/status

    Feature Branch (only applies to dev):

        MAXAR_ARD_HOSTNAME = ard-dev.maxar.com
        ARD_DEV_BRANC = new_kml

        ard_url('select', 'status') -> https://ard-dev.maxar.com/api/v1/select-new_kml/status

    """
    hostname = os.environ.get("MAXAR_ARD_HOSTNAME", "ard.maxar.com/api/v1")
    dev_branch = os.environ.get("ARD_DEV_BRANCH")
    if dev_branch:
        return f'https://{hostname}/{args[0]}-{dev_branch}/{"/".join(args[1:])}'
    else:
        return f'https://{hostname}/{args[0]}/{"/".join(args[1:])}'


AUTH_URL = ard_url("auth", "authenticate")

_USER_SESSION_CACHE = None
_CLIENT_SESSION_CACHE = {}


def get_self(session):
    """Fetch the account SELF endpoint of the current user

    Parameters
    ----------
    session : OAuth2Session
        The session object created for the current user

    Returns
    -------
    dict: SELF api payload"""

    r = session.get(ard_url("auth", "self"))
    r.raise_for_status()
    return r.json()


def get_session():
    warnings.warn(
        "get_session() will be deprecated for the more specific get_user_session()",
        DeprecationWarning,
    )
    return get_user_session()


def add_session_hooks(session):
    """
    Add hooks for session object, and return it.
    Note: Order of Hooks is important.
    """
    session.hooks["response"] = [
        # Specific 400 errors
        bad_geom_request_hook,
        # Generic 400 errors
        bad_ard_request_hook,
        # 413 errors
        oversize_request_hook,
        # 403 errors
        unauth_request_hook,
        # 404 errors
        missing_resource_hook,
        # non-200 errors
        ard_server_request_hook,
    ]

    return session


def get_user_session():
    """Get an authenticated Requests session for communicating with the ARD API

    Example
    -------
    >>> r = get_user_session()
    >>> resp = r.get('https://ard-dev.geobigdata.io/api/v1/select/request/5542092796671610498')

    Returns
    -------
    OAuth2Session
        Authenticated Requests session

    Notes
    -----
    For credentials, create a file in your home directory called .ard-config with these contents:

        [ard]
        user_name = <your_user_name>
        user_password = <your_password>

    or set these environment variables:

        ARD_USERNAME
        ARD_PASSWORD
    """
    global _USER_SESSION_CACHE
    if _USER_SESSION_CACHE is None:
        _USER_SESSION_CACHE = _get_user_session()
    return _USER_SESSION_CACHE


def _get_user_session(config_file=None):
    """Get an authenticated Requests session for communicating with the ARD API

    Parameters
    ----------
    config_file, optional
        Path to config file

    Returns
    -------
    OAuth2Session
        Authenticated Requests session

    Notes
    -----
    If you provide ARD_ACCESS_TOKEN and ARD_REFRESH_TOKEN via env vars it will
    use those credentials.  If you provide a path to a config
    file, it will look there for the credentials. If you don't it will try to
    pull the credentials from environment variables (ARD_USERNAME, ARD_PASSWORD).
    If that fails and you have a '~/.ard-config' ini file, it will read from that.
    """

    session = None
    if os.environ.get("ARD_ACCESS_TOKEN", None):
        session = session_from_existing_token(
            access_token=os.environ.get("ARD_ACCESS_TOKEN", None),
            refresh_token=os.environ.get("ARD_REFRESH_TOKEN", None),
        )

    # If no config file specified, try using environment variables.  If that
    # fails and there is a config in the default location, use that.
    if not session and not config_file:
        try:
            session = session_from_envvars()
        except MissingTokenError as e:
            raise Exception("Invalid ARD credentials given in environment variables.")
        except Exception as e:
            config_file = os.path.expanduser("~/.ard-config")

    example_credentials = """
    [ard]
    user_name = your_user_name
    user_password = your_password
    """

    if config_file and not os.path.isfile(config_file):
        raise Exception(
            f"Please create a ARD credential file at ~/.ard-config with these contents:\n{example_credentials}"
        )

    if not session:
        try:
            session = session_from_config(config_file)
        except:
            raise Exception(
                "Invalid credentials or incorrectly formated config file at ~/.ard-config"
            )

    session = mount_adaptors(session)
    return add_session_hooks(session)


def get_client_session(client_id=None, client_secret=None):
    """Get an authenticated session using client credentials (Maxar internal only)

    If a client ID and secret are not passed as kwargs, the env vars
    ARD_CLIENT_ID and ARD_CLIENT_SECRET will be used if they exist."""

    global _CLIENT_SESSION_CACHE
    if _CLIENT_SESSION_CACHE[client_id] is None:
        _CLIENT_SESSION_CACHE[client_id] = _get_client_session(
            client_id=client_id, client_secret=client_secret
        )

    return _CLIENT_SESSION_CACHE


def _get_client_session(client_id=None, client_secret=None):
    """Get an authenticated session using client credentials (Maxar internal only)

    If a client ID and secret are not passed as kwargs, the env vars
    ARD_CLIENT_ID and ARD_CLIENT_SECRET will be used if they exist."""

    token_url = f"{AUTH_URL}/oauth2/token"

    if not client_id:
        client_id = os.environ.get("ARD_CLIENT_ID")
    if not client_secret:
        client_secret = os.environ.get("ARD_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Unable to find credentials")

    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id=client_id)

    # set up our OAuth session
    oauth = OAuth2Session(
        client=client, scope=["com.maxar.ard/ard.search", "com.maxar.ard/ard.order"]
    )

    token = oauth.fetch_token(token_url=token_url, auth=auth)

    return mount_adaptors(oauth)


def session_from_existing_token(access_token, refresh_token="no_refresh_token", auth_url=AUTH_URL):
    """Get a session using an existing access_token and refresh_token.

    Parameters
    ----------
    access_token : str
        Access token
    refresh_token : str
        Refresh token

    Returns
    -------
    OAuth2Session
        Authenticated Requests session
    """

    def save_token(token):
        s.token = token

    token = {
        "token_type": "Bearer",
        "refresh_token": refresh_token,
        "access_token": access_token,
        "scope": ["read", "write"],
        "expires_in": 604800,
        "expires_at": 0,
    }

    # grab the expiration from the jwt access_token. Don't verify because
    # we dont care about source of token. ARD auth endpoint will handle that.
    try:
        t = jwt.decode(access_token, verify=False)
    except DecodeError:
        raise Exception(
            "Supplied ARD access token is not a valid JWT.  Check ARD_ACCESS_TOKEN env var or runtime.json"
        )
    token["expires_at"] = t["exp"]

    s = OAuth2Session(
        token=token,
        auto_refresh_url=auth_url,
        token_updater=save_token,
    )

    return s


def session_from_envvars(
    auth_url=AUTH_URL,
    environ_template=(("username", "ARD_USERNAME"), ("password", "ARD_PASSWORD")),
):
    """Returns a session with the ARD authorization token baked in,
    pulling the credentials from environment variables.

    environ_template - An iterable of key, value pairs. The key should
                      be the variables used in the oauth workflow, and
                      the values being the environment variables to
                      pull the configuration from.  Change the
                      template values if your envvars differ from the
                      default, but make sure the keys remain the same.
    Returns
    -------
    OAuth2Session
        Authenticated Requests session
    """

    def save_token(token):
        s.token = token

    client_id = "dummyclientid"
    client_secret = "dummyclientsecret"

    environ = {var: os.environ[envvar] for var, envvar in environ_template}
    s = OAuth2Session(
        client=LegacyApplicationClient(client_id),
        auto_refresh_url=auth_url,
        auto_refresh_kwargs={"client_id": client_id, "client_secret": client_secret},
        token_updater=save_token,
    )

    s.fetch_token(auth_url, **environ)

    return s


def session_from_kwargs(**kwargs):
    """Get a  session object using credentials from keywords

    Parameters
    ----------
    **kwargs : dict
        Authentication keywords: username, password, client_id, client_secret

    Returns
    -------
    OAuth2Session
        Authenticated Requests session
    """

    def save_token(token):
        s.token = token

    auth_url = AUTH_URL
    s = OAuth2Session(
        client=LegacyApplicationClient(kwargs.get("client_id")),
        auto_refresh_url=auth_url,
        auto_refresh_kwargs={
            "client_id": kwargs.get("client_id"),
            "client_secret": kwargs.get("client_secret"),
        },
        token_updater=save_token,
    )

    try:
        s.fetch_token(
            auth_url,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            client_id=kwargs.get("client_id"),
            client_secret=kwargs.get("client_secret"),
        )
    except MissingTokenError as e:
        raise Exception("Invalid credentials passed into session_from_kwargs()")

    return s


def session_from_config(config_file):
    """Get a  session object using credentials from a config file

    Parameters
    ----------
    config_file : str
        path to config file

    Returns
    -------
    OAuth2Session
        Authenticated Requests session
    """

    def save_token(token_to_save):
        """Save off the token back to the config file."""
        if not SAVE_TOKEN:
            return
        if not "ard_token" in set(cfg.sections()):
            cfg.add_section("ard_token")
        cfg.set("ard_token", "json", json.dumps(token_to_save))
        with open(config_file, "w") as sink:
            cfg.write(sink)

    # Read the config file (ini format).
    cfg = ConfigParser(interpolation=None)
    if not cfg.read(config_file):
        raise RuntimeError("No ini file found at {} to parse.".format(config_file))
    client_id = "dummy_client_id(not-required)"
    client_secret = "dummy_client_secret(not-required)"

    # the ini file has the optional ability to set an auth url (useful for dev)
    if not cfg.has_option("ard", "auth_url"):
        auth_url = AUTH_URL
    else:
        auth_url = cfg.get("ard", "auth_url")

    # See if we have a token stored in the config, and if not, get one.
    if "ard_token" in set(cfg.sections()):
        # Parse the token from the config.
        token = json.loads(cfg.get("ard_token", "json"))

        s = OAuth2Session(
            client_id,
            client=LegacyApplicationClient(client_id, token=token),
            auto_refresh_url=auth_url,
            auto_refresh_kwargs={"client_id": client_id, "client_secret": client_secret},
            token_updater=save_token,
        )
        s.token = token
        # hit the server to trigger a refresh if the token has expired
        try:
            s.get(ard_url("auth", "self"))
            return s
        except MissingTokenError:
            pass

    # No pre-existing token or the refresh expired, so we request one from the API.
    s = OAuth2Session(
        client_id,
        client=LegacyApplicationClient(client_id),
        auto_refresh_url=auth_url,
        auto_refresh_kwargs={"client_id": client_id, "client_secret": client_secret},
        token_updater=save_token,
    )

    # Get the token and save it to the config.
    token = s.fetch_token(
        auth_url,
        username=cfg.get("ard", "user_name"),
        password=cfg.get("ard", "user_password"),
        client_id=client_id,
        client_secret=client_secret,
        auth=False,
    )
    save_token(token)

    return s


def write_config(username, password):
    """Write a config file

    The config file will be written to ~/.ard-config.

    Parameters
    ----------
    username : str
        Username
    password: str
        Password
    """

    config_file = os.path.expanduser("~/.ard-config")
    cfg = ConfigParser()
    cfg.read(config_file)

    # create or update ard section
    if "ard" not in cfg.sections():
        cfg["ard"] = {}
    if username:
        cfg["ard"]["user_name"] = username
    if password:
        cfg["ard"]["user_password"] = password

    # reset the token
    cfg.remove_section("ard_token")

    with open(config_file, "w") as configfile:
        cfg.write(configfile)


def read_token():
    """Read the token from the config file

    Returns
    -------
    str
        Access token
    """

    config_file = os.path.expanduser("~/.ard-config")
    cfg = ConfigParser()
    cfg.read(config_file)
    print(json.loads(cfg["ard_token"]["json"])["access_token"])
