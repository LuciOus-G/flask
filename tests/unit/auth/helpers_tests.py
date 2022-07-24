from __future__ import unicode_literals, absolute_import
import base64
import os
import unittest
from collections import namedtuple

from faker import Factory
from flask import Flask, g
from mock import MagicMock, patch
from nose.tools import istest, raises
from flask_appsfoundry.auth.helpers import credentials_from_request, \
    assert_user_permission, UnauthorizedError as Unauthorized, assert_user_has_any_permission, UnauthorizedError

fake = Factory.create()


@istest
class AssertUserPermissionTests(unittest.TestCase):

    def test_user_permissions_valid(self):
        """ Method should return None if the user has valid permissions.
        """
        required_perms = ['perm1', 'perm2', 'perm3']
        self.assertIsNone(assert_user_permission(required_perms, user_perm=['perm2']))

    @raises(Unauthorized)
    def test_user_permissions_invalid(self):
        required_perms = ['perm1', 'perm2', 'perm3']
        assert_user_permission(required_perms, user_perm=['perm4'])

    @raises(Unauthorized)
    def test_anonymous_user(self):
        required_perms = ['perm1', 'perm2', 'perm3']
        assert_user_permission(required_perms, user_perm=None)


UserInfo = namedtuple('UserInfo', ['username', 'token', 'user_id', 'perm'])
ANONYMOUS_USER = UserInfo(username='anonymous', token=None, user_id=0, perm=[])


class AssertUserHasAnyPermissionTests(unittest.TestCase):

    env_testing = os.environ.get('TESTING', None)
    this_app = Flask(__name__)
    from flask_babel import Babel
    Babel(this_app)

    @classmethod
    def setUpClass(cls):
        # remove testing from environment so we can test the method
        os.environ.pop('TESTING', None)

    @classmethod
    def tearDownClass(cls):
        # restore the condition
        if cls.env_testing:
            os.environ['TESTING'] = cls.env_testing

    def test_user_permission_valid(self):
        """test method assert_user_has_any_permission in scoop flask"""
        with self.this_app.test_request_context('/'):
            required_perms = ['perm1', 'perm2', 'perm3']
            g.user = UserInfo(username=fake.user_name(), token=fake.password(), user_id=fake.pyint(), perm=['perm2'])
            self.assertIsNone(assert_user_has_any_permission(
                required_perms, redis=None, app_conf={}))

    @raises(UnauthorizedError)
    def test_user_permissions_invalid(self):
        with self.this_app.test_request_context('/'):
            required_perms = ['perm1', 'perm2', 'perm3']
            g.user = UserInfo(username=fake.user_name(), token=fake.password(), user_id=fake.pyint(), perm=['perm4'])
            assert_user_has_any_permission(required_perms, redis=None, app_conf={})

    @raises(UnauthorizedError)
    def test_anonymous_user(self):
        with self.this_app.test_request_context('/'):
            required_perms = ['perm1', 'perm2', 'perm3']
            g.user = ANONYMOUS_USER
            assert_user_has_any_permission(required_perms, redis=None, app_conf={})


class Method_credentials_from_request_Tests(unittest.TestCase):
    """ Checks the credentials_from_request auth helper method to make sure that
    failures of auth always return the expected exception type
    (:py:class:`werkzeug.exceptions.Unauthorized`), and good requests return the expected
    decoded username and password.
    """
    def setUp(self):
        self.app = Flask(__name__)
        from flask_babel import Babel
        Babel(self.app)

    def test_missing_auth_headers_raise_unauthorized(self):
        """ Unauthorized raised if no Authorization header provided. """

        with self.app.test_request_context('/') as ctx:
            headers = MagicMock(spec=dict)
            headers.attach_mock(MagicMock(side_effect=KeyError), '__getitem__')

            ctx.request.headers = headers

            self.assertRaises(Unauthorized, credentials_from_request)

    def test_auth_header_without_bearer_raises_unauthorized(self):
        """ The value for Authorization header must contain 2 space-delimited
        values.
        """
        headers = {
            'Authorization': "".join(fake.random_letter() for _ in range(20))}

        with self.app.test_request_context('/', headers=headers):
            self.assertRaises(Unauthorized, credentials_from_request)

    def test_auth_header_with_incorrect_bearer_raises_unauthorized(self):
        """ Authorization header value must start with 'Bearer'
        """
        headers = {
            'Authorization': "NotAValidBearer {0}".format("".join(fake.random_letter() for _ in range(20)))}

        with self.app.test_request_context('/', headers=headers):
            self.assertRaises(Unauthorized, credentials_from_request)

    def test_credentials_decode_failure_raises_unauthorized(self):
        """ Authorization header value must be base-64 encoded. """
        not_base64_encoded = "{0}:{0}".format("".join(fake.random_letter() for _ in range(20)))
        headers = {
            'Authorization': 'Bearer {0}'.format(not_base64_encoded)
        }

        with self.app.test_request_context('/', headers=headers):
            self.assertRaises(Unauthorized, credentials_from_request)

    def test_blank_username_password_raises_unauthorized(self):
        """ If username or password is blank, Unauthorized should be raised. """
        for i in range(1):

            rand_text = "".join(fake.random_letter() for _ in range(20))

            username = rand_text if i else ""
            password = rand_text if not i else ""

            auth_val = base64.b64encode("{0}:{1}".format(username, password).encode())

            headers = {
                'Authorization': 'Bearer {0}'.format(auth_val)
            }
            with self.app.test_request_context('/', headers=headers):
                self.assertRaises(Unauthorized, credentials_from_request)

    def test_success_returns_username_password_tuple(self):
        """ Username, password tuple are returned when a valid Authorization.
        header is present.
        """
        username = fake.user_name()
        password = "".join(fake.random_letter() for _ in range(20))

        token = base64.b64encode("{0}:{1}".format(username, password).encode())

        headers = {
            'Authorization': 'Bearer {0}'.format(token)
        }

        with self.app.test_request_context('/', headers=headers):
            decoded_username, decoded_password = credentials_from_request()

            self.assertEquals(decoded_username, username)
            self.assertEquals(decoded_password, password)


