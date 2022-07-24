"""
Filter Inputs
=============

These instances are designed to be used with the corresponding
SqlAlchemyFilterParser class to define your expected input parameters
and how they are parsed into objects.
"""
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
from warnings import warn

from flask_restful import inputs
from six import text_type

from .operators import EqualTo, NotEqualTo, LessThan, GreaterThan, \
    LessThanOrEqual, GreaterThanOrEqual, InCollection, NotInCollection, \
    CaseInsensitiveLike, CaseSensitiveLike, Contains


__all__ = [
    'FilterField', 'BooleanFilter', 'DateTimeFilter', 'EnumFilter', 'IntegerFilter', 'StringFilter', 'DecimalFilter',
]


class FilterField(object):
    """
    An argument used specifically with the FilterArgsParser class.
    It expects most of the same argument as the StandardArgs parser,
    however also accepts 2 additional constructor arguments:

    * default_operator - defaults to 'eq', but can be set to any of the other supposed operators.
    * multi_format - 'csv' or 'multi_arg'
    """
    operators = (EqualTo, NotEqualTo, )
    sqlalchemy_column = None
    _default_operator = 'eq'
    _default_multiarg_format = 'csv' # or multiarg


    @property
    def default_operator(self):
        return filter(lambda e: e.input_suffix == self._default_operator, self.operators)[0]

    def __init__(self, **kwargs):
        """
        :param `callable` type:
            Single-arg callable, that will be used to convert the input argument into the proper type.
        """
        self.default = kwargs.pop('default', None)
        self.dest = kwargs.pop('dest', None)
        self.type = kwargs.pop('type', text_type)
        self.location = kwargs.pop('location', ('json', 'values'))
        self.choices = kwargs.pop('choices', ())
        self.help = kwargs.pop('help', None)
        self.case_sensitive = kwargs.pop('case_sensitive', True)
        self.multi_format = kwargs.pop('multi_format', self._default_multiarg_format)
        self._default_operator = kwargs.pop('default_operator', self._default_operator)

        self.check_and_warn_for_unsupported_args(kwargs)

    @staticmethod
    def check_and_warn_for_unsupported_args(args):
        """
        This method should be called only by the constructor of the base
        filter field.  This will issue a warning if any unsupported arguments
        are left in the \*\*kwargs dictionary (note: if overriding init,
        pop any arguments you want to override off of kwargs, unless they\'re
        part of the constructor for your base object).

        :param dict args: Dictionary of input arguments (presumably to init)
        """
        for arg in args:
            warn("Unsupported kwarg ({}) passed to FilterField. "
                 "Only a subset of InputField kwargs are supported with "
                 "FilterInput".format(arg))


class IntegerFilter(FilterField):
    """
    Parses input arguments as an integer.

    Supports the following operators:

    * eq
    * ne
    * lt
    * lte
    * gt
    * gte
    * in
    * notin
    * contains - (only if the underlying collection is a list)!
    """
    operators = (EqualTo,
                 NotEqualTo,
                 LessThan,
                 LessThanOrEqual,
                 GreaterThan,
                 GreaterThanOrEqual,
                 InCollection,
                 NotInCollection,
                 Contains,
                 )

    def __init__(self, **kwargs):
        kwargs['type'] = int
        super(IntegerFilter, self).__init__(**kwargs)


class DateTimeFilter(FilterField):
    """
    Filters an incoming request and parses it's input as an ISO8601 formatted
    string.

    Supports the following operations:

    * eq
    * ne
    * lt
    * lte
    * gt
    * gte
    """
    operators = (EqualTo,
                 NotEqualTo,
                 LessThan,
                 LessThanOrEqual,
                 GreaterThan,
                 GreaterThanOrEqual
                 )

    def __init__(self, **kwargs):
        kwargs['type'] = inputs.datetime_from_iso8601
        super(DateTimeFilter, self).__init__(**kwargs)


class BooleanFilter(FilterField):
    """
    Parses an input string as a boolean.  True, true, 1 will all parse as True,
    while False, false, and 0 will all evaluate to false.

    Supports the following operations:

    * eq
    * ne
    """
    def __init__(self, **kwargs):
        kwargs['type'] = inputs.boolean
        super(BooleanFilter, self).__init__(**kwargs)


class EnumFilter(FilterField):
    """
    Supports our dirty, dirty practice of parsing magic numbers in requests
    into proper sqlalchemy enums (well.. really unicode strings.. then hashed to create enums!).

    Supports the following operations:

    * eq
    * ne
    * in
    """
    operators = (EqualTo,
                 NotEqualTo,
                 InCollection,
                 )

    def __init__(self, enum=None, **kwargs):
        """
        :param dict enum: integer-key, string-valued dictionary where they keys are assumed to be the APIs representation of the value, and the values are assumed to be strings used as enums in a Postgres column.
        :param callable type: Single-arg callable, that will be used to convert the input argument into the proper type.
        """
        self.enum = enum or {}
        kwargs['type'] = lambda val: self.enum[int(val)]
        super(EnumFilter, self).__init__(**kwargs)


class StringFilter(FilterField):
    """
    Parses input as a unicode string.

    Supports the following operators:

    * eq
    * ne
    * ilike (case-insensitive like)
    * like (case-sensitive like)

    Also please note, the ilike and like queries behave as %yourquery%, if
    the request does not contain any placeholders.
    """
    operators = (EqualTo,
                 NotEqualTo,
                 CaseInsensitiveLike,
                 CaseSensitiveLike,
                 )


class DecimalFilter(IntegerFilter):
    def __init__(self, **kwargs):
        kwargs['type'] = Decimal
        super(IntegerFilter, self).__init__(**kwargs)



