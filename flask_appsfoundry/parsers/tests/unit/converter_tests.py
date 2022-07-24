from __future__ import absolute_import, unicode_literals
from base64 import b64encode
from datetime import datetime
import unittest
import random
import json

from faker import Factory
from nose.tools import raises
from werkzeug.exceptions import BadRequest

from flask_appsfoundry.parsers.converters import (
    decodedimage_from_b64string, DecodedImage, sqlalchemy_orderby_statement, iso3166_country, iso639_language,
    naive_datetime_from_iso8601, address_from_json
)
from tests.fixtures.images import base_64_encoded_images


fake = Factory.create()


class DecodedImageTests(unittest.TestCase):

    def test_decode_image(self):
        imgs = [decodedimage_from_b64string(s) for s in base_64_encoded_images]
        for img in imgs:
            # PIL uses old-style classes for images .. so this test won't work because img.image
            # is always an instance type:
            # self.assertIsInstance(img.image, Image)
            self.assertRegexpMatches(
                img.short_filename, r"^[a-zA-Z0-9]+\.[a-zA-Z0-9]{3,4}$")
            self.assertIsInstance(img, DecodedImage)

    @raises(BadRequest)
    def test_bad_b64_input(self):
        not_b64_string = "".join(fake.random_letter() for _ in range(100))
        decodedimage_from_b64string(not_b64_string)

    @raises(BadRequest)
    def test_non_image_input(self):
        random_string = "".join(fake.random_letter() for _ in range(100))
        b64_string = b64encode(random_string)
        decodedimage_from_b64string(b64_string)


class Iso3166Tests(unittest.TestCase):

    def test_valid_country(self):
        for cc in ['ID', 'id', 'IDN', 'idn']:
            result = iso3166_country(cc)
            self.assertEqual(cc, result)

    @raises(BadRequest)
    def test_invalid_country(self):
        not_a_country_code = "XYZ"
        iso3166_country(not_a_country_code)


class Iso639Tests(unittest.TestCase):

    def test_valid_language(self):
        for lc in ['EN', 'en', 'ENG', 'eng']:
            result = iso639_language(lc)
            self.assertEqual(lc, result)

    @raises(BadRequest)
    def test_invalid_language(self):
        not_a_language_code = "XYZ"
        iso639_language(not_a_language_code)


class NaiveDateTimeFromISO8601Tests(unittest.TestCase):

    @raises(BadRequest)
    def test_date_only(self):
        input = "2015-03-27"
        naive_datetime_from_iso8601(input)

    def test_year_and_week(self):
        input = "2015-W01-4T00:00:00+00:00"
        result = naive_datetime_from_iso8601(input)
        self.assertEqual(datetime(2015, 1, 1, 0, 0, 0), result)

    def test_no_timezone(self):
        input = "2015-03-27T21:07:46"
        result = naive_datetime_from_iso8601(input)
        self.assertEqual(datetime(2015, 3, 27, 21, 7, 46), result)

    def test_timezone_lessthan_utc(self):
        input = "2015-03-27T21:07:46-05:00"
        result = naive_datetime_from_iso8601(input)
        self.assertEqual(datetime(2015, 3, 28, 2, 7, 46), result)

    def test_timezone_greatthan_utc(self):
        input = "2015-03-27T21:07:46+01:00"
        result = naive_datetime_from_iso8601(input)
        self.assertEqual(datetime(2015, 3, 27, 20, 7, 46), result)

class AddressFromJsonTests(unittest.TestCase):

    def test_from_dict(self):
        input = {'address1': fake.street_address(),
                 'address2': fake.street_suffix(),
                 'city': fake.city(),
                 'state': fake.state(),
                 'postal_code': fake.postcode(),
                 'country_code': fake.country_code()}
        result = address_from_json(input)

        for k in result:
            self.assertEqual(input[k], result[k])

    def test_from_string(self):

        input = {'address1': fake.street_address(),
                 'address2': fake.street_suffix(),
                 'city': fake.city(),
                 'state': fake.state(),
                 'postal_code': fake.postcode(),
                 'country_code': fake.country_code()}

        str_input = json.dumps(input)

        result = address_from_json(str_input)

        for k in result:
            self.assertEqual(input[k], result[k])

    def test_insufficient_values(self):

        input = {'address1': fake.street_address(),
                 'address2': fake.street_suffix(),
                 'city': fake.city(),
                 'state': fake.state(),
                 'postal_code': fake.postcode(),
                 'country_code': fake.country_code()}

        # randomly set some of the keys in input, to None
        for key in input:
            if random.choice([True, False]):
                input[key] = None

        result = address_from_json(input)

        for k in result:
            self.assertEqual(input[k], result[k])

    def test_extra_values(self):

        input = {'address1': fake.street_address(),
                 'address2': fake.street_suffix(),
                 'city': fake.city(),
                 'state': fake.state(),
                 'postal_code': fake.postcode(),
                 'country_code': fake.country_code()}

        # randomly add 5 extra values to the dictionary
        for random_key in [fake.word() for _ in range(5)]:
            if random_key not in input:
                input[random_key] = fake.word()

        result = address_from_json(input)

        self.assertEqual(len(result), 6)

        for k in ['address1', 'address2', 'city', 'state', 'postal_code', 'country_code']:
            self.assertEqual(input[k], result[k])


class SqlAlchemyOrderByStatementTests(unittest.TestCase):

    def test_ascending_order(self):
        input = "id"
        result = sqlalchemy_orderby_statement(input)
        self.assertEqual(input, result)

    def test_descending_order(self):
        input = "-id"
        result = sqlalchemy_orderby_statement(input)
        self.assertEqual(result, "id desc")



