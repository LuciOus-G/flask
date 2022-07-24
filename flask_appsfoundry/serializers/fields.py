"""
General purpose serializers fields/nested that are not tied to any specific
"""
from __future__ import absolute_import, unicode_literals
from calendar import timegm
from datetime import datetime
from email.utils import formatdate

import pytz

from flask_restful.fields import *
from flask_restful.fields import MarshallingException


__all__ = [
    'String', 'FormattedString', 'Url', 'DateTime', 'Float', 'Integer', 'Arbitrary', 'Nested', 'List', 'Raw',
    'Boolean', 'Fixed', 'Price', 'DateTime', 'EnumFieldFormatter', 'IdNameSerializer'
]


class DateTime(Raw):
    """
    Return a formatted datetime string in UTC. Supported formats are RFC 822
    and ISO 8601.

    See :func:`email.utils.formatdate` for more info on the RFC 822 format.

    See :meth:`datetime.datetime.isoformat` for more info on the ISO 8601
    format.

    :param dt_format: ``'rfc822'`` or ``'iso8601'``
    :type dt_format: str
    """
    def __init__(self, dt_format='rfc822', **kwargs):
        super(DateTime, self).__init__(**kwargs)
        self.dt_format = dt_format

    def format(self, value):
        try:
            if self.dt_format == 'rfc822':
                return _rfc822(value)
            elif self.dt_format == 'iso8601':
                return _iso8601(value)
            else:
                raise MarshallingException(
                    _('Unsupported date format {date_format}').format(date_format=self.dt_format)
                )
        except AttributeError as ae:
            raise MarshallingException(ae)


def _rfc822(dt):
    """Turn a datetime object into a formatted date.
    Example::
        fields._rfc822(datetime(2011, 1, 1)) => "Sat, 01 Jan 2011 00:00:00 -0000"
    :param dt: The datetime to transform
    :type dt: datetime
    :return: A RFC 822 formatted date string
    """
    return formatdate(timegm(dt.utctimetuple()))


def _iso8601(dt):
    """Turn a datetime object into an ISO8601 formatted date.
    Example::
        fields._iso8601(datetime(2012, 1, 1, 0, 0)) => "2012-01-01T00:00:00+00:00"
    :param dt: The datetime to transform
    :type dt: datetime
    :return: A ISO 8601 formatted date string
    """
    return datetime.isoformat(
        datetime.fromtimestamp(timegm(dt.utctimetuple()), tz=pytz.UTC)
    )


class EnumFieldFormatter(Raw):
    '''
    Converts an input string, into it's banner type integer value.
    '''
    def __init__(self, enum_dict, *args, **kwargs):
        self.enum_dict = enum_dict
        super(EnumFieldFormatter, self).__init__(*args, **kwargs)

    def format(self, value):
        """
        Returns an integer representation of a string value.

        :param string value:
        :return: Returns the integer value for a given string field.
        :rtype: int
        """
        try:
            for key, val in self.enum_dict.items():
                if val == value:
                    return key
        except KeyError:
            raise MarshallingException(underlying_exception=KeyError)


class IdNameSerializer(Raw):

    def format(self, value):
        return {'id': value.id, 'name': value.name,}
