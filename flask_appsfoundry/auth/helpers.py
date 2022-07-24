from __future__ import absolute_import, unicode_literals
import base64
import logging
import os

from flask import request, g

from flask_appsfoundry import exceptions
from .constants import TOKEN_PREFIX


class UnauthorizedError(exceptions.Unauthorized):

    def __init__(self, message):
        super(UnauthorizedError, self).__init__(
            user_message=message, developer_message=message)


def assert_user_permission(required_permissions, user_perm):
    """ Check if the current user any of the required permissions.

    If the user has any of the permissions, this check will pass and return
    nothing.

    When this application is running in 'test' mode, these checks will be
    disabled and a warning will be issued.

    :param iterable of strings required_permissions: List of permissions that
        the user's permissions will be checked against.
    :param `list` user_perm: The user permission information to use for Authorization.
    :return: None if the check passes.
    :raises: :class:`UnauthorizedError` if the user does
        not have any of the required permissions.
    """
    if user_perm and any([req_perm in user_perm for req_perm in required_permissions]):
        pass
    else:
        raise UnauthorizedError("Token {}, Invalid Permissions".format(
            "Invalid" if not user_perm else "Valid"
        ))


def assert_user_has_any_permission(required_permissions, redis=None, app_conf={},
                                   token_prefix=TOKEN_PREFIX, req=request):
    """
    Check if the current user has any permissions in a set of required
    permissions.  If the user has any of the permissions, this check will
    pass.

    :param iterable of strings required_permissions: List of permissions that
        the user's permissions will be checked against.
    :param redis: Redis instance that will be queried.
    :param dict app_conf: Current flask application config.
    :param req: Current flask request object.
    :return: None if the check passes.
    :raises: :class:`UnauthorizedError` if the user does
        not have any of the required permissions.
    """

    # If testing mode is enabled, then we disable auth checks
    if os.environ.get('TESTING'):
        logging.warning("TESTING mode enabled.  "
                        "Authorization checks are disabled.")
        return

    assert_user_permission(required_permissions=required_permissions,
                           user_perm=g.user.perm if g.user and g.user.perm else None)


def credentials_from_request(req=request):
    """
    Attempts to retrieve the Username and (hashed) Password from our
    expected Oauth2 Bearer-style headers.

    :param :py:class:`flask.Request` req: Current request object.
    :return: Username, Password from Auth header
    :rtype: tuple(string, string)
    :raises: :class:`UnauthorizedError` if unable to decode
        Authorization header, or headers are missing, or in an incorrect format.
    """
    try:
        auth_header = req.headers['Authorization']

        (bearer, token) = auth_header.split(' ')

        # sanity check -- we always expect the auth header to include 'Bearer'
        if not bearer == 'Bearer':
            raise UnauthorizedError("Incorrect Authorization header")

        # Decode the token passed in the Bearer portion
        decoded = base64.b64decode(token)
        (username, password) = decoded.split(":")

        # Make sure either the username or password is not blank
        if '' in (username, password):
            raise UnauthorizedError("Invalid Bearer token")

        return username, password

    except KeyError:
        raise UnauthorizedError("Missing Authorization Header")

    except (ValueError, TypeError):
        raise UnauthorizedError("Bearer decode failed")


