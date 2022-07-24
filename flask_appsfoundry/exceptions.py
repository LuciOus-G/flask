"""
Scoop Exceptions
================

A module containing exception classes that can be raised directly from Flask that will return a JSON formatted
error message.

All of our error messages follow the same, basic format.

.. code-block:: HTTP

    {
        "status": 500,
        "error_code": 5001010,
        "devloper_message": "Message to a dev that's debugging.",
        "user_message": "Some message that should be displayed by the front end."
    }

"""
from __future__ import absolute_import, unicode_literals
import json

from flask_babel import gettext as _, ngettext

from six.moves.http_client import (
    NOT_FOUND, UNAUTHORIZED, FORBIDDEN, CONFLICT, BAD_REQUEST, UNPROCESSABLE_ENTITY, EXPECTATION_FAILED, PROCESSING,
    NOT_ACCEPTABLE, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED
)
from werkzeug import exceptions as wzexc


class ScoopApiException(wzexc.HTTPException):
    """ A JSON-formatted exception message that should be the base of all errors raised by SCOOP APIs.

    It's basic format is as follows.
    """
    def __init__(self, code=None, error_code=None, user_message=None, developer_message=None):
        """
        :param `int` code:
            The HTTP status code that's returned with the response.  This should exactly match the
            HTTP status_code to be returned.
        :param `int` error_code:
            A micro error code to help developers determine more closely the exact source of the problem.
        :param `six.string_types` user_message:
            The message that should be shown to the end user.  Be extremely careful with what you put here!
        :param `six.string_types` developer_message:
            The message that should be shown to developers who are debugging/logging their application.
        """

        self.code = code or 500
        self.error_code = error_code or 500
        self.user_message = user_message or _("An unknown error occurred.")
        self.developer_message = developer_message or "Backend didn't set a message.  Please complain to us =)."
        self.response = None
        self.description = developer_message

    def get_body(self, environ=None):
        """Get the exception response body as a JSON document."""
        return json.dumps({
            "status": self.code,
            "error_code": self.error_code,
            "user_message": self.user_message,
            "developer_message": self.developer_message
        })

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    def __str__(self):
        return '%d: %s' % (self.code, self.__class__.__name__)

    def __repr__(self):
        return '<%s \'%s\'>' % (self.__class__.__name__, self)


class NotFound(ScoopApiException, wzexc.NotFound):
    def __init__(self, **kwargs):
        super(NotFound, self).__init__(
            code=NOT_FOUND,
            error_code=NOT_FOUND,
            user_message=kwargs.get("user_message", _("The requested resource could not be found")),
            developer_message=kwargs.get("developer_message", "The requested resource could not be found")
        )


class InternalServerError(ScoopApiException, wzexc.InternalServerError):
    def __init__(self, **kwargs):
        super(InternalServerError, self).__init__(
            code=INTERNAL_SERVER_ERROR,
            error_code=INTERNAL_SERVER_ERROR,
            user_message=kwargs.get("user_message", _('The server encountered an internal error.')),
            developer_message=kwargs.get("developer_message", 'The server encountered an internal error.')
        )


class Conflict(ScoopApiException, wzexc.Conflict):
    def __init__(self, **kwargs):
        super(Conflict, self).__init__(
            code=CONFLICT,
            error_code=CONFLICT,
            user_message=kwargs.get("user_message", _("The request conflicts with the server.")),
            developer_message=kwargs.get("developer_message", "The request conflicts with the server.")
        )


class Unauthorized(ScoopApiException):
    def __init__(self, **kwargs):
        super(Unauthorized, self).__init__(
            code=UNAUTHORIZED,
            error_code=UNAUTHORIZED,
            user_message=kwargs.get("user_message",
                                    _('You cannot access this resource with the provided credentials.')),
            developer_message=kwargs.get("developer_message",
                                         "You cannot access this resource with the provided credentials.")
        )


class Forbidden(ScoopApiException):
    def __init__(self, **kwargs):
        super(Forbidden, self).__init__(
            code=FORBIDDEN,
            error_code=FORBIDDEN,
            user_message=kwargs.get("user_message", _("You cannot access this resource.")),
            developer_message=kwargs.get("developer_message", "You cannot access this resource.")
        )


class BadRequest(ScoopApiException):
    def __init__(self, **kwargs):
        super(BadRequest, self).__init__(
            code=BAD_REQUEST,
            error_code=BAD_REQUEST,
            user_message=kwargs.get("user_message", _("Your request couldn't be understood by the server.")),
            developer_message=kwargs.get("developer_message", "Your request couldn't be understood by the server.")
        )


class UnprocessableEntity(ScoopApiException):
    def __init__(self, **kwargs):
        super(UnprocessableEntity, self).__init__(
            code=UNPROCESSABLE_ENTITY,
            error_code=UNPROCESSABLE_ENTITY,
            user_message=kwargs.get("user_message", _("Your request contained invalid data.")),
            developer_message=kwargs.get("developer_message", "Your request contained invalid data.")
        )


class ExpectationFailed(ScoopApiException):
    def __init__(self, **kwargs):
        super(ExpectationFailed, self).__init__(
                code=EXPECTATION_FAILED,
                error_code=EXPECTATION_FAILED,
                user_message=kwargs.get("user_message", _("Expectation failed")),
                developer_message=kwargs.get("developer_message", "Expectation failed")
            )


class Processing(ScoopApiException):
    def __init__(self, **kwargs):
        super(Processing, self).__init__(
                code=PROCESSING,
                error_code=PROCESSING,
                user_message=kwargs.get("user_message", _("Operation is still processing.")),
                developer_message=kwargs.get("developer_message", "Operation is still processing.")
            )


class ScoopConfigError(Exception):
    """ An exception that indicates our application configuration is invalid.
    This should be raised by our startup_checks module and should prevent the
    application from loading completely.
    """
    pass


class NotAcceptable(ScoopApiException):
    def __init__(self, **kwargs):
        super(NotAcceptable, self).__init__(
            code=NOT_ACCEPTABLE,
            error_code=NOT_ACCEPTABLE,
            user_message=kwargs.get("user_message", _("Invalid ACCEPT mimetype")),
            developer_message=kwargs.get("developer_message", "Invalid ACCEPT mimetype")
        )


class MethodNotAllowed(ScoopApiException):
    def __init__(self, **kwargs):
        super(MethodNotAllowed, self).__init__(
            code=METHOD_NOT_ALLOWED,
            error_code=METHOD_NOT_ALLOWED,
            user_message=kwargs.get("user_message", _("Method not allowed")),
            developer_message=kwargs.get("developer_message", "Method not allowed")
        )
