from __future__ import absolute_import, unicode_literals
import unittest
import random

from flask_appsfoundry.parsers import SqlAlchemyFilterParser

from tests.fixtures.parsers import EmployeeListParser, EmployeeAlternateListParser
from tests.fixtures.models import EMPLOYEE_JOBS, HOURLY_EMPLOYEE
from tests.fixtures.testutils.parsers import test_app


class SqlAlchemyFilterParserTests(unittest.TestCase):

    def test_exception_raised_if_model_missing(self):
        """ Instances of SqlAlchemyFilterParser must define __model__ attribute before instantiation.
        """
        given = SqlAlchemyFilterParser
        self.assertIsNone(given.__model__, None)
        self.assertRaises(ValueError, given)

    def test_instantiation(self):
        """
        Make sure FilterField subclasses defined on class-level properties
        are assigned to __fields__ dictionary of parser instance, keyed by
        their attribute name.
        """
        # given a simple parser class
        parser_class = EmployeeListParser

        # when instantiated
        parser = parser_class()

        # then, it's class attributes that inherit from "FilterField" should
        #   be removed and stored under the __fields__ dictionary.
        for name in ['id', 'is_active']:
            self.assertNotIn(name, vars(parser))
            self.assertIn(name, parser.__fields__)

    def test_explicit_eq_operator(self):
        """
        Given: A simple filter_parser class
            and a parser -- that matches the simple model class.
            and a request -- ?id__eq=3&is_active__eq=true
        When: Arguments are parsed
        Then: All arguments in request should be returened in a dictionary,
            and they should be stored without the explicit __eq suffix.
            Ex, ?id__eq=3 -> {'id': <SqlAlchemyBinaryExpression(left.value:3)>,}
        NOTE: Checks against is_active are disabled because the right variable
            of the binary expression does not contain a value attribute when
            run against a boolean column.
        """
        # given a simple parser class
        parser = EmployeeListParser()

        with test_app.test_request_context("?id__eq=3&is_active__eq=true"):
            # when request args are parsed
            args = parser.parse_args().pop('filters')

            # then, there should be 2 arguments returned, one for each
            # arg in the query string, and the suffix (__eq) should be dropped.
            self.assertEqual(len(args), 2)
            for name in ['id', 'is_active']:
                bin_exprs = filter(lambda x: x.left.name == name, args)
                self.assertEqual(len(bin_exprs), 1)

    def test_implicit_default_operator(self):

        parser = EmployeeListParser()

        with test_app.test_request_context("?id=3&is_active=false"):
            args = parser.parse_args().pop('filters')

            self.assertEqual(len(args), 2)
            for name in ['id', 'is_active']:
                bin_exprs = filter(lambda x: x.left.name == name, args)
                self.assertEqual(len(bin_exprs), 1)

    def test_dest(self):

        # given
        parser = EmployeeAlternateListParser()

        opt = random.choice(EMPLOYEE_JOBS.keys())

        # when
        with test_app.test_request_context("?job_id={}".format(opt)):
            args = parser.parse_args().pop('filters')

            self.assertEqual(len(args), 1)

            job_arg = args.pop()

            self.assertEqual(job_arg.left.name, 'job')
            self.assertEqual(job_arg.right.value, EMPLOYEE_JOBS[opt])

