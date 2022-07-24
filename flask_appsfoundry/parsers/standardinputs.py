from __future__ import unicode_literals, absolute_import
from decimal import Decimal

from six import text_type
from werkzeug.exceptions import BadRequest

from .arguments import NestedJsonParserArgument
from .converters import decodedimage_from_b64string, natural, positive, naive_datetime_from_iso8601, boolean

# TODO: warn on unknown parameters

__all__ = ['InputField', 'IntegerField', 'PositiveIntegerField',
           'Base64ImageField', 'CSVField', 'NaturalNumberField',
           'StringField', 'EnumField', 'BooleanField', 'DateTimeField',
           'DecimalField', ] # 'NestedField', ]


class InputField(object):
    def __init__(self, **kwargs):
        self.default = kwargs.pop('default', None)
        self.dest = kwargs.pop('dest', None)
        self.required = kwargs.pop('required', False)
        self.ignore = kwargs.pop('ignore', False)
        self.type = kwargs.pop('type', text_type)
        self.location = kwargs.pop('location', ('json', 'values'))
        self.choices = kwargs.pop('choices', ())
        self.action = kwargs.pop('action', 'store')
        self.help = kwargs.pop('help', None)
        self.operators = kwargs.pop('operators', ('=', ))
        self.case_sensitive = kwargs.pop('case_sensitive', True)
        self.store_missing = kwargs.pop('store_missing', True)


class StringField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = text_type
        super(StringField, self).__init__(**kwargs)


class IntegerField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = int
        super(IntegerField, self).__init__(**kwargs)


class PositiveIntegerField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = positive
        super(PositiveIntegerField, self).__init__(**kwargs)


class NaturalNumberField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = natural
        super(NaturalNumberField, self).__init__(**kwargs)


class Base64ImageField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = decodedimage_from_b64string
        super(Base64ImageField, self).__init__(**kwargs)


class CSVField(InputField):
    def __init__(self, **kwargs):
        # action = append always
        self.inner_type = kwargs.pop('type', text_type)
        kwargs['type'] = self.parse_csv
        super(CSVField, self).__init__(**kwargs)

    def parse_csv(self, input):
        return [self.inner_type(inner)
                for inner in input.split(',')]


class EnumField(InputField):
    def __init__(self, enum_dict, **kwargs):
        self.enum_dict = enum_dict
        kwargs['type'] = self.convert_enum
        super(EnumField, self).__init__(**kwargs)

    def convert_enum(self, input):
        try:
            return self.enum_dict[input]
        except KeyError:
            raise BadRequest(description=u"Invalid value: {}".format(input))


class DateTimeField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = naive_datetime_from_iso8601
        super(DateTimeField, self).__init__(**kwargs)


class BooleanField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = boolean
        super(BooleanField, self).__init__(**kwargs)


class DecimalField(InputField):
    def __init__(self, **kwargs):
        kwargs['type'] = Decimal
        super(DecimalField, self).__init__(**kwargs)

# from collections import namedtuple
# from werkzeug.datastructures import MultiDict
# from flask import request
#
# FakeRequest = namedtuple('FakeRequest', ['unparsed_arguments', 'json'])

class NestedJsonField(InputField):
    def __init__(self, inner_class, **kwargs):
        self.parser_inst = inner_class(argument_class=NestedJsonParserArgument)
        kwargs['type'] = self.parse_nested
        super(NestedJsonField, self).__init__(**kwargs)

    def parse_nested(self, *args, **kwargs):



        for arg in self.parser_inst.args:
            pass

        return self.parser_inst.parse_args(*args, **kwargs)
