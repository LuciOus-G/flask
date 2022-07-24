from __future__ import absolute_import, unicode_literals
import unittest

from mock import MagicMock
from werkzeug.exceptions import NotAcceptable, BadRequest, Unauthorized, \
    NotFound

from flask_appsfoundry.controllers.base import ErrorHandlingApiMixin


class MethodWrappingTests(unittest.TestCase):

    def test_expected_methods_wrapped(self):

        class FakeApi(ErrorHandlingApiMixin):
            def head(self):
                raise Exception("Meh")
            def get(self):
                raise Exception("Meh")
            def post(self):
                raise Exception("Meh")
            def put(self):
                raise Exception("Meh")
            def delete(self):
                raise Exception("Meh")

        fake_api = FakeApi()

        for meth_name in ['head', 'get', 'post', 'put', 'delete']:

            # quick sanity check to make sure the methods we're
            # testing are actually supposed to be wrapped.
            self.assertIn(meth_name, fake_api.wrapped_http_methods)

            method = getattr(fake_api, meth_name)
            try:
                method()
            except Exception:
                self.fail("{0} should not reraise an"
                          " Exception".format(meth_name))

        # if we made it here, our test has passed
        self.assertTrue(True)


class ErrorRoutingTests(unittest.TestCase):

    def test_error_handling_by_code(self):
        """
        Errors that contain a code property should route to a method called
        _handle_{number_of_code}, if it exists.
        """
        class FakeApi(ErrorHandlingApiMixin):
            def __init__(self):
                self.get = MagicMock(side_effect=NotAcceptable)
                self._handle_406 = MagicMock()
                super(FakeApi, self).__init__()

        fake_api = FakeApi()
        fake_api.get()

        self.assertEqual(fake_api._handle_406.call_count, 1)

    def test_error_handling_by_code_is_preferred(self):

        class FakeApi(ErrorHandlingApiMixin):
            def __init__(self):
                self.get = MagicMock(side_effect=NotAcceptable)
                self._handle_NotAcceptable = MagicMock()
                self._handle_406 = MagicMock()
                super(FakeApi, self).__init__()

        fake_api = FakeApi()
        fake_api.get()

        self.assertEqual(fake_api._handle_NotAcceptable.call_count, 0)

    def test_error_handling_by_name(self):

        class FakeApi(ErrorHandlingApiMixin):
            def __init__(self):
                self.get = MagicMock(side_effect=NotAcceptable)
                self._handle_NotAcceptable = MagicMock()
                super(FakeApi, self).__init__()

        fake_api = FakeApi()
        fake_api.get()

        self.assertEqual(fake_api._handle_NotAcceptable.call_count, 1)

    def test_error_handling_catchall(self):

        class FakeApi(ErrorHandlingApiMixin):
            def __init__(self):
                self.get = MagicMock(side_effect=NotAcceptable)
                self._handle_all = MagicMock()
                super(FakeApi, self).__init__()

        fake_api = FakeApi()
        fake_api.get()

        self.assertEqual(fake_api._handle_all.call_count, 1)

    def test_response_400_401_404_format(self):
        """
        Our predefined exceptions should all return this expected format.
        """
        for exc in [BadRequest, Unauthorized, NotFound, Exception]:

            class FakeApi(ErrorHandlingApiMixin):
                def __init__(self):
                    self.get = MagicMock(side_effect=exc)
                    super(FakeApi, self).__init__()

            fake_api = FakeApi()
            response, code = fake_api.get()

            for expected_key in ['status', 'error_code',
                                 'user_message', 'developer_message']:
                self.assertIn(expected_key, response)

    def test_expected_error_codes(self):

        exc_and_error_code = [
            (BadRequest, 400101),
            (NotFound, 404),
            (Unauthorized, 401101),
        ]

        for exc, expected_code in exc_and_error_code:

            class FakeApi(ErrorHandlingApiMixin):
                def __init__(self):
                    self.get = MagicMock(side_effect=exc)
                    super(FakeApi, self).__init__()

            fake_api = FakeApi()
            response, http_status_code = fake_api.get()

            self.assertEqual(response['error_code'], expected_code)
            self.assertEqual(response['status'], exc.code)
            self.assertEqual(response['status'], http_status_code)

    def test_catchall_defaults_to_http_500(self):
        """
        Exceptions that don't contain a 'code', should always default to
        HTTP 500.
        """
        class FakeApi(ErrorHandlingApiMixin):
            def __init__(self):
                self.get = MagicMock(side_effect=Exception)
                super(FakeApi, self).__init__()

        fake_api = FakeApi()
        response, code = fake_api.get()

        self.assertEqual(code, 500)


class OtherTests(unittest.TestCase):

    def test_before_error_dispatch_called(self):
        """
        query_set.session.rollback should always be called, regardless
        of whether the transaction succeeds or fails.
        """
        for side_effect in [Exception, BadRequest]:
            class FakeApi(ErrorHandlingApiMixin):
                def __init__(self):
                    self.get = MagicMock(side_effect=side_effect)
                    self._before_error_dispatch = MagicMock()
                    super(FakeApi, self).__init__()

            fake_api = FakeApi()
            fake_api.get()

            self.assertEqual(fake_api._before_error_dispatch.call_count, 1)
