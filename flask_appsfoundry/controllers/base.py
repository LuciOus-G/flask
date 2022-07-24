"""
Base Controllers
================

These mixins are very abstract and have no mechanisms themselves for
dispatching HTTP requests.  They're here to handle all the things that
are required all of our HTTP dispatching controllers/mixins defined
in ``standard`` and ``dynamic``.
"""
from __future__ import absolute_import, unicode_literals
import warnings
from six.moves.http_client import OK, BAD_REQUEST, UNAUTHORIZED, INTERNAL_SERVER_ERROR, NOT_FOUND

from flask_appsfoundry import viewmodels
from flask_appsfoundry.parsers import specialized
from flask_appsfoundry.helpers import get_or_create_instance


class ErrorHandlingApiMixin(object):
    """
    Controller mixin that catches specific error types, and generates
    a view model for our error message data.

    This is used to preempt the error handing inside of Flask-Restful 0.3,
    because it does not allow us full control over error message formats.

    This mixin achieves this by automatically wrapping ALL methods listed
    inside of 'wrapped_http_methods' with the 'format_scoop_error' method.
    Whenever an exception is raised, the wrapper will try to lookup
    and appropriate method to handle that error method:

    * _handle_{code} - All standard werkzeug exception classes have a code
        associated with them (for example, BadRequest has a code of 400).
    * _handle_{name} - Will try to match a handler based on the class name
        of the exception instance thrown.
    * _handle_all - If no suitable error method has been found, this method
        will be called.  It will return an HTTP 500.

    By default, the following types of errors will be handled: 400, 401, 404.
    If you need additional error handlers, they can be defined on your
    controller by adding a method named _handle_418(self, exception) or
    _handle_ImATeapotException(self, exception).

    This method will also attempt to rollback any existing transaction, by
    calling the _rollback_transaction(self, query_set) method.
    """
    wrapped_http_methods = ('head', 'get', 'post', 'put', 'delete', )

    def __init__(self, *args, **kwargs):

        super(ErrorHandlingApiMixin, *args, **kwargs)

        # Manually wrap API methods with our error handler.
        for http_method_name in self.wrapped_http_methods:

            http_method = getattr(self, http_method_name, None)

            if http_method is not None:
                setattr(self,
                        http_method_name,
                        self.format_scoop_error(http_method))

    def format_scoop_error(self, func):
        '''
        Wrapper function for a controller endpoint method
        (get, put, delete, etc...)

        It should be used for catching our specific error message formats,
        and returning those.

        :param func: The python function to wrap.
        :return: The wrapped function.
        '''
        def internal(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as e:

                code = getattr(e, 'code', 500)

                candidate_handler_names = [
                    "_handle_{code}".format(code=code),
                    "_handle_{name}".format(name=type(e).__name__),
                    "_handle_all"
                ]
                candidate_handler_names = [m for m in candidate_handler_names if hasattr(self, m)]

                self._before_error_dispatch()

                handler = getattr(self, candidate_handler_names[0])

                return handler(e)

        return internal

    def _before_error_dispatch(self):
        """
        Called before dispatching to any of the _handle_{some_error_or_code}.
        This should be used to tie up any loose ends (like rolling back the
        current transaction).
        """
        warnings.warn("There was an error encountered, but no handler was configured")

    def _handle_400(self, exception):

        data = getattr(exception, 'data', {})

        response = {
            "status": BAD_REQUEST,
            "error_code": 400101,
            "user_message": data.get('user_message', str(exception)),
            "developer_message": data.get('developer_message',
                                          "No developer message")
        }

        return response, BAD_REQUEST

    def _handle_401(self, exception):

        response = {
            "status": UNAUTHORIZED,
            "error_code": 401101,
            "user_message": str(exception),
            "developer_message": getattr(exception, 'description', "Unauthorized")
        }

        return response, UNAUTHORIZED

    def _handle_404(self, exception):

        response = {
            'status': NOT_FOUND,
            'error_code': NOT_FOUND,
            'user_message': 'Not found',
            'developer_message': str(exception)
        }

        return response, NOT_FOUND

    def _handle_all(self, exception):
        """
        Catch-all error handler for any error codes that are not otherwise
        explicitly defined.  Errors will be returned with HTTP 500.
        """
        code = getattr(exception, 'code', INTERNAL_SERVER_ERROR)

        response = {
            'status': code,
            'error_code': code,
            'user_message': 'A problem occurred, please try again.',
            'developer_message': str(exception)
        }

        return response, code


class DbSetApiMixin(ErrorHandlingApiMixin):
    """
    Common base mixin for any controllers that primarially interact with
    a single type from a SQLAlchemy data store.

    The following class-level attributes may be set:

    query_set
        **required.**  A sqlalchemy base query (ie, in our situation, something
        like (Item.query))
    """

    query_set = None
    response_serializer = None
    field_limiting_parser = specialized.FieldLimitingParser()
    attribute_column_mapping = {}
    viewmodel = viewmodels.SaViewmodelBase
    field_expanding_parser = specialized.FieldExpandingParser()
    expandable_field_serializers = {}

    def _get_viewmodel(self, model):
        return get_or_create_instance(self.viewmodel, model)


    def _get_serializer(self):

        # instantiate the response serializer.
        # this really always needs to be
        serializer = get_or_create_instance(self.response_serializer)

        # strip out fields that we don't want
        serializer = self._limit_serializer_fields(serializer)

        # add extra fields
        serializer = self._append_serializer_fields(serializer)

        return serializer

    def _limit_serializer_fields(self, serializer):
        """

        :param serializer:
        :return:
        """
        # delete unwanted fields from serializer
        fields_parser = get_or_create_instance(self.field_limiting_parser)
        fields = fields_parser.parse_args()['fields']

        # ?fields=all is assumed to mean we want all the fields
        if 'all' not in fields:
            # create a temporary list of attribute names
            all_fields = [key for key, value in serializer.items()]
            for attr_name in all_fields:
                if attr_name not in fields:
                    delattr(serializer, attr_name)
        return serializer

    def _append_serializer_fields(self, serializer):

        # ?expand=csv field again
        expand_parser = get_or_create_instance(self.field_expanding_parser)
        fields_to_expand = expand_parser.parse_args()['expand']
        # expanding all
        if 'ext' in fields_to_expand:
            fields_to_expand = self.expandable_field_serializers.keys()

        for expand_name in fields_to_expand:
            expand_serializer = self.expandable_field_serializers[expand_name]
            serializer.__serializer_fields__[expand_name] = expand_serializer

        return serializer

    def _before_error_dispatch(self):
        """
        If we leave an aborted transaction, Flask-SQLAlchemy will NOT
        remove it on request teardown.. and it will hang all subsequent
        requests.  If your query set it coming from somewhere else other than
        self.query_set, you MUST override this method!
        """
        try:
            self.query_set.session.rollback()
        except Exception:
            warnings.warn("Could not rollback session")
