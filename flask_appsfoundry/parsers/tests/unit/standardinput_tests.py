import unittest
from datetime import datetime, timedelta
from faker import Factory
from flask.ext.appsfoundry.parsers.standardinputs import CSVField, \
    Base64ImageField, EnumField, DateTimeField, BooleanField
from flask.ext.appsfoundry.parsers.converters import DecodedImage
from six import text_type
from tests.fixtures.images import base_64_encoded_images
import random
fake = Factory.create()

class CSVFieldTests(unittest.TestCase):

    def test_unicode_inner(self):

        random_strings = [fake.word() for _ in range(10)]

        field = CSVField()
        results = field.type(",".join(random_strings))

        self.assertEquals(len(results), 10)
        for r in results:
            self.assertIsInstance(r, text_type)
            self.assertIn(r, random_strings)

    def test_integer_inner(self):

        random_ints = [fake.pyint() for _ in range(10)]

        field = CSVField(type=int)
        results = field.type(",".join([str(n) for n in random_ints]))

        self.assertEquals(len(results), 10)
        for r in results:
            self.assertIsInstance(r, int)
            self.assertIn(r, random_ints)



class Base64ImageFieldTests(unittest.TestCase):

    def test_base_64_input(self):
        input = random.choice(base_64_encoded_images)
        field = Base64ImageField()
        result = field.type(input)
        self.assertIsInstance(result, DecodedImage)

class EnumFieldTests(unittest.TestCase):

    def test_conversion(self):
        enum_dict = {1: 'a', 2: 'b', }
        field = EnumField(enum_dict=enum_dict)

        key = random.choice(enum_dict.keys())
        result = field.type(key)

        self.assertEqual(result, enum_dict[key])

class DateTimeFieldTests(unittest.TestCase):

    def test_convert_now(self):

        curr_time = datetime.now()

        input = curr_time.isoformat()
        field = DateTimeField()
        result = field.type(input)

        # milliseconds will be stripped -- account for
        self.assertAlmostEqual(result, curr_time, delta=timedelta(seconds=1))

class BooleanFieldTests(unittest.TestCase):

    def test_convert_bool(self):
        input = fake.pybool()
        field = BooleanField()
        result = field.type(input)

        self.assertEqual(result, input)

    def test_convert_text(self):
        input = random.choice(["false", "True"])
        field = BooleanField()
        result = field.type(input)

        if input == "false":
            self.assertFalse(result)
        else:
            self.assertTrue(result)

    def test_convert_int(self):
        input = random.choice([0, 1])
        field = BooleanField()
        # as of fr 0.3.2, integer inputs must be string-encoded
        result = field.type(str(input))

        if input == 0:
            self.assertFalse(result)
        else:
            self.assertTrue(result)

