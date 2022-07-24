import unittest

from tests.fixtures.parsers import EmployeeParserBase

from faker import Factory

fake = Factory.create()


class StandardParserTests(unittest.TestCase):

    def test_default_type(self):
        p = EmployeeParserBase()
        name_arg = filter(lambda e: e.name == 'first_name', p.args)[0]
        any_name = fake.first_name()
        result = name_arg.type(any_name)
        self.assertEqual(any_name, result)

    def test_integer_type(self):
        p = EmployeeParserBase()
        id_arg = filter(lambda e: e.name == 'id', p.args)[0]
        any_number = fake.pyint()
        result = id_arg.type(any_number)
        self.assertEqual(any_number, result)
