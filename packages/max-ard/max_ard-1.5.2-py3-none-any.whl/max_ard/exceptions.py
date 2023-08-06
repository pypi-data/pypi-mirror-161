""" ARD Exceptions """

from datetime import datetime

#########
# General Errors
#########


class MissingDependency(Exception):
    """A dependency required for this functionality has not been installed"""

    pass


#########
# API Errors
#########


class ARDServerException(Exception):
    """The ARD API service encountered an error"""

    def __init__(self, msg, *args, **kwargs):
        msg = f"{msg} ({datetime.now()})"
        super().__init__(msg, *args, **kwargs)


class BadARDRequest(Exception):
    """The ARD API request sent was incorrectly formatted"""

    pass


class MissingARDResource(Exception):
    """An ARD API request returned a 404"""

    pass


class MissingSummary(MissingARDResource):
    """Summary data for a requested cell does not exist.
    The cell needs to be registered with the metadata service."""

    pass


class GeometryException(Exception):
    """The ARD API request sent was incorrectly formatted"""

    pass


class OversizeRequestException(Exception):
    """The ARD API request sent was incorrectly formatted"""

    pass


class UnAuthorizedException(Exception):
    """The ARD API request sent had bad creds"""

    pass


class NotSubmitted(Exception):
    """A Select or Order has not been submitted"""

    pass


class NotFinished(Exception):
    """A select has not finished running so results are not available yet"""

    pass


class SelectError(Exception):
    """Errors returned from the Select Service"""

    pass


class NotSuccessful(Exception):
    """Error in processing"""

    pass


#########
# IO Errors
#########


class UnknownFileType(Exception):
    """A file input was not recognized as a readable format"""

    pass


#######
# S3 Storage Errors
#######


class BucketInitError(Exception):
    """An error occured initializing an S3 bucket"""

    pass


class BucketRevokeError(Exception):
    """An error occured initializing an S3 bucket"""

    pass


########
# Hook functions for Request.Session.hooks
########


def oversize_request_hook(r, *args, **kwargs):
    """
    Hook for handling oversize request errors from API.
    """
    if r.status_code == 413 and "Request Entity Too Large" in r.json()["message"]:
        raise OversizeRequestException(
            f'{r.json()["message"]}, Reduce size of attributes and try again.'
        )

    return r


def bad_geom_request_hook(r, *args, **kwargs):
    """
    Hook for handling bad geometry errors from API.
    """
    if r.status_code == 400 and "Problem with intersects/bbox" in r.json()["message"]:
        raise GeometryException(r.json()["message"])

    return r


def bad_ard_request_hook(r, *args, **kwargs):
    """
    Hook for handling 400 errors from API.
    """
    if r.status_code == 400:
        raise BadARDRequest(r.json()["message"])

    return r


def unauth_request_hook(r, *args, **kwargs):
    """
    Hook for handling 401 errors from API.
    """
    if r.status_code == 401:
        raise UnAuthorizedException(
            f"Server response was {r.json()['message']}, check your credentials and try again."
        )

    return r


def missing_resource_hook(r, *args, **kwargs):
    if r.status_code == 404:
        raise MissingARDResource(r.json()["message"])

    return r


def ard_server_request_hook(r, *args, **kwargs):
    """
    Hook for handling non-20X errors from API.
    """
    if not r.ok:
        raise ARDServerException(r.json()["message"])

    return r
