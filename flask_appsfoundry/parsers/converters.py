"""
Converters
==========
This module contains helper functions used along with our Parser (link to me)
as they type for InputField attributes to parse
(and in some cases, provide some light validation) of incoming data.

These functions all take a single argument (assumed to be a unicode
string), and return any python data type.

Also note, this is logically the same thing as the methods found in
Flask-RESTful's inputs module, so all those methods are imported and
exposed here as well.

Failed Conversions
------------------
If conversion fails, these methods must raise a
:py:class:`werkzeug.exceptions.BadRequest` exception, and providing
the **description** keyword argument to explain what failed.

See Also

- https://flask-restful.readthedocs.org/en/0.3.1/api.html#module-reqparse
- http://flask-restful.readthedocs.org/en/latest/api.html#module-inputs

Available Converters
--------------------
"""
from __future__ import absolute_import, unicode_literals
import base64
from collections import namedtuple
import hashlib
import json
import os
from re import compile

from flask_restful import inputs
from iso3166 import countries
import iso639
from PIL import Image
import six
from six import StringIO
from werkzeug.exceptions import BadRequest

# DO NOT REMOVE -- exposing Flask-RESTful's inputs module here
from flask.ext.restful.inputs import *


DecodedImage = namedtuple('DecodedImage', ['image', 'short_filename'])


def decodedimage_from_b64string(input):
    """
    Returns a DecodedImage object (named tuple with two attributes: image,
    a PIL Image object, and a short_filename string).

    :param str base64_input: A base-64 encoded string containin image data.
    :return: An in-memory DecodedImage object.
    :rtype: :py:class:`DecodedImage`
    :raises: :py:class:`werkzeug.exceptions.BadRequest`
    """
    try:
        decoded_data = base64.b64decode(input)

        # if we're in python 3, StringIO is going to require a string, not a bytestring
        if six.PY3:
            decoded_data = decoded_data.decode()

        image = Image.open(StringIO(decoded_data))
        filename = "{base_name}.{ext}".format(
            base_name=hashlib.sha1(input).hexdigest(),
            ext=image.format).lower()

        return DecodedImage(image=image, short_filename=filename)

    except Exception as e:
        raise BadRequest(description="Error decoding image: {}".format(str(e)))


def iso3166_country(input):
    """
    Makes sure that a given input is a valid ISO3166 country code.  If it is,
    then the same input will be returned.

    :param str input: An ISO3166 country code (either alpha 2 or 3)
    :return: The exact same argument that was provided.
    :rtype: str
    :raises: :py:class:`werkzeug.exceptions.BadRequest`
    """
    try:
        countries.get(input)
    except KeyError:
        raise BadRequest(
            description="{country_code} is not a valid ISO "
                        "3166 country code".format(country_code=input))

    return input


def iso639_language(input):
    """
    Makes sure that a given input is a valid ISO639 language code.  If valid,
    the same string will be returned as was provided as an argument.

    :param str input: An ISO639 language code (either alpha 2 or 3b/t)
    :return: The exact same argument that was provided.
    :rtype: str
    :raises: :py:class:`werkzeug.exceptions.BadRequest`
    """
    # only matches on lower-case values
    if iso639.find(input.lower()) is not None:
        return input
    else:
        raise BadRequest("{input} is not a valid ISO 639 language code".
                         format(input=input))


def naive_datetime_from_iso8601(input):
    """
    Parses an ISO 8601 string, and returns a naive datetime object, converted
    to UTC time.  Input must be an ISO8601 DateTime object (input without a
    TIME component will raise a BadRequest exception), in either
    year-month-day format or year-week-dayofweek format.  Specifying a timezone
    is supported, and the returned input will always be in UTC.

    The following are all valid:

    * "2015-W01-4T00:00:00Z" - New Year's Day, 2015 in UTC
    * "2015-03-27T21:07:46" - March 27th, 2015 @ 9:07:46 PM UTC
    * "2015-03-27T21:07:46-05:00" - Same as previous, but in Pittsburgh.. where
        it's only 4PM.

    :param str input: An ISO-8601 Date/Time encoded string.
    :return: A naive datetime object, that's been calculated in UTC.
    :rtype: datetime.datetime
    :raises: :py:class:`werkzeug.exceptions.BadRequest`
    """
    # the datetime_from_iso8601 doesn't follow RequestParser's documented
    # expected exception types.  If a really wrong input comes in here, it
    # raises a ValueError, so we catch it and reraise a BadRequest exception.
    try:
        aware = inputs.datetime_from_iso8601(input)
    except ValueError:
        raise BadRequest(
            description=u"{input_value} is not a valid ISO 8601 date time"
            .format(input_value=input))

    # datetime_from_iso8601 always returns times in UTC, so we're
    # safe to just strip the tz component
    if aware.tzinfo:
        aware = aware - aware.utcoffset()
    naive = aware.replace(tzinfo=None)
    return naive


def address_from_json(input):
    """
    Parses out a dictionary representing a standard postal address from either
    another dictionary or an input string.  Missing keys will be set a None,
    and unexpected keys will be skipped.  Values of the dictionary are all
    strings, and no additional validation si provided.

    :param input: A dictionary, or a string encoded json object
        containing address information.
    :type input: str or dict
    :return: A dictionary representing a standard postal address.  Contains
        the keys: address1, address2, city, state, postal_code, country_code
    :rtype: dict
    :raise: :py:class:`werkzeug.exceptions.BadRequest`
    """
    addr = {
        'address1': None,
        'address2': None,
        'city': None,
        'state': None,
        'postal_code': None,
        'country_code': None,
    }

    try:

        if isinstance(input, six.string_types):
            input = json.loads(input)

        for key in addr:
            addr[key] = input.get(key)

    except (ValueError, KeyError) as e:
        raise BadRequest(description=str(e))

    return addr


def sqlalchemy_orderby_statement(input):
    """
    Returns a string that can be passed to a SQL Alchemy query's order_by
    method.  It is assumed that the input will contain only the name of a field,
    and that field will be prefixed with a minus symbol (-) to indicate
    descending.

    :param str input: a field name, optionally prefixed with minus (-).
    :return: A string suitable for passing to a SQLAlchemy order_by method.
    :rtype: str
    """
    regex = compile(r"^(?P<desc>-)?(?P<field_name>.+)$")
    is_desc, field_name = regex.match(input).groups()
    return "{0} desc".format(field_name) if is_desc else field_name


class ImageFieldParser(object):
    """
    Handles upload input parsing for image data.
    Decodes and saves the image to a given path (with a filename based on
    the file data's SHA1 hash and an extension based on the image format).
    """
    def __init__(self, save_directory):
        """
        Creates a new instance of ImageFieldParser
        Raises an exception if the directory path does not already exist.
        :param str save_directory: The full path to where images
            should be saved.
        :raises: :py:class:`ValueError` if save_directory does not exist.
        """
        self.save_directory = save_directory

        if not os.path.exists(self.save_directory):
            raise ValueError("save_directory ({path}) does not exist!".format(
                path=self.save_directory))

    def from_base64(self, base64_input):
        """
        Returns a filename (not the full path) of an image.
        The base64_input will be decoded and saved to the file system, in
        whichever save_directory was passed to the constructor.
        WARNING: This has the side-effect of IMMEDIATELY saving the image
        data to disk!
        :param str base64_input: A base-64 encoded string containin image data.
        :return: A string short (no directory path) filename the image has
            been saved as.
        :rtype: str
        :raises: :py:class:`werkzeug.exceptions.BadRequest`
        """
        try:
            decoded_data = base64.b64decode(base64_input)
            # if we're in python 3, StringIO is going to require a string, not a bytestring
            if six.PY3:
                decoded_data = decoded_data.decode()
            strh = StringIO(decoded_data)
            img = Image.open(strh)
        except Exception as e:
            raise BadRequest("Error decoding image: {message}".
                             format(message=str(e)))

        # create a name for the image -- based on it's SHA1 hash
        # and an extension based on the image data format
        file_name = "{base_name}.{ext}".format(
            base_name=hashlib.sha1(base64_input).hexdigest(),
            ext=img.format).lower()
        full_path = os.path.join(self.save_directory, file_name)

        # if the image already exists, then we skip saving it to the
        # filesystem
        if not os.path.exists(full_path):
            img.save(full_path)

        return file_name


class ScoopCasClientIdField(object):
    """
    Parse scoopcas client_id's from an input string, and
    verifies that the client_id is actually valid from scoopcas
    """
    def __init__(self, service):
        """
        :param :py:class:`app.services.scoopcas.ScoopCas` service: The service
            instance that will be used for communicating with ScoopCas to
            validate our provided token
        """
        self.service = service

    def client_id(self, value):
        """
        Takes the input value as a client_id that can be looked-up in scoopcas.
        :param str|int value: A single value that indicates the client ID.
            This may either already be an integer, or a string-encoded integer.
        :return: An integer parsed from the provided value.
        :rtype: int
        :raises: :py:class:`werkzeug.exceptions.BadRequest`
        """
        try:
            client_id = int(value)
        except ValueError:
            raise BadRequest("{value} is not a valid client id".
                             format(value=value))

        try:
            client_info = self.service.get_client(client_id)
            return client_info['id']
        except Exception as e:
            raise BadRequest(str(e))
