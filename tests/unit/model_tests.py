import re
from unittest import TestCase

from faker import Faker
from mock import MagicMock
from werkzeug import exceptions

from flask.ext.appsfoundry.models import SoftDeletableMixin
from flask.ext.appsfoundry.controllers.base import ErrorHandlingApiMixin


fake = Faker()


class ErrorResponseFormatterTests(TestCase):

    def test_BadRequest_is_handled(self):

        handler = ErrorHandlingApiMixin()

        funct = MagicMock(side_effect=exceptions.BadRequest)
        funct = handler.format_scoop_error(funct)
        resp, code = funct()

        # just make sure status and response set
        self.assertIsNotNone(resp)
        self.assertIsNotNone(code)

    def test_status_and_response_code_should_match(self):
        '''
        We're indicating the error code by the HTTP status
        code, but we're also setting the error code in the
        json response body.  Make sure these always match.
        '''
        handler = ErrorHandlingApiMixin()

        funct = MagicMock(side_effect=exceptions.BadRequest)
        funct = handler.format_scoop_error(funct)
        resp, code = funct()

        self.assertEqual(resp['status'], code)

    def test_handled_errors_have_expected_format(self):
        '''
        '''
        handler = ErrorHandlingApiMixin()

        for ex in [exceptions.BadRequest]:
            funct = MagicMock(side_effect=ex)
            funct = handler.format_scoop_error(funct)
            resp, code = funct()

            # make sure that we get returned our expected error
            # code, and the response contains all our expected
            # keys.  In this case, we're not interested in checking
            # what they're set to.
            self.assertIsNotNone(resp['status'])
            self.assertIsNotNone(resp['developer_message'])
            self.assertIsNotNone(resp['error_code'])
            self.assertIsNotNone(resp['user_message'])



class ScoopModelMixinTests(TestCase):

    def test_has_expected_prefix(self):
        '''
        Make sure that the prefix of core_ is appended to automatically-named
        tables.
        '''
        class MobileDerekModel(SoftDeletableMixin):
            pass

        md = MobileDerekModel()

        pattern = re.compile(r'^(?P<prefix>core_)(?P<tablename>.*)$',
                             re.IGNORECASE|re.DOTALL)

        results = pattern.search(md.__tablename__)

        actual_prefix = results.groupdict()['prefix']
        expected = "core_"

        self.assertEqual(actual_prefix, expected)


    def test_returns_pluralized_table_name(self):
        '''
        Very naive attempt to make sure that our tablenames are in plural form.
        '''
        class MobileDerekModel(SoftDeletableMixin):
            pass

        md = MobileDerekModel()

        pattern = re.compile(r'^(?P<prefix>core_)(?P<tablename>.*)$',
                             re.IGNORECASE|re.DOTALL)

        results = pattern.search(md.__tablename__)

        actual_tablename = results.groupdict()['tablename']
        expected = \
            "{tablename}{suffix}".format(
                tablename="mobilederekmodel",
                suffix="s")

        self.assertEqual(actual_tablename, expected)

    def test_is_lowercase(self):
        '''
        Automatically-generated tablenames should contain no upper-case
        characters.
        '''
        class MobileDerekModel(SoftDeletableMixin):
            pass

        md = MobileDerekModel()

        pattern = re.compile(r'[A-Z]')
        results = pattern.search(md.__tablename__)
        self.assertIsNone(results)

    def test_can_override_autotablename(self):
        """
        Manually-defined __tablename__ in a derrived class will take presidence
        over the auto-generated table names.
        """
        random_table_name = ''.join([fake.random_letter() for _ in range(20)])

        class MobileDerekModel(SoftDeletableMixin):
            __tablename__ = random_table_name

        md = MobileDerekModel()

        self.assertEqual(md.__tablename__, random_table_name)
