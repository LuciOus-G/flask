from __future__ import absolute_import, unicode_literals

from flask import request
from flask_restful import reqparse
from six import with_metaclass
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .arguments import ErrorHandlingArgument
from .filterinputs import FilterField, BooleanFilter, DateTimeFilter, IntegerFilter, StringFilter, DecimalFilter
from .standardinputs import InputField

__all__ = ['ParserBase', 'SqlAlchemyFilterParser', 'reqparse', ]


class ParserMeta(type):
    """ Rewrites any FilterField from the class-level into a special dictionary called __parser_args__.
    """
    def __new__(cls, name, parents, dct):
        input_fields = ParserMeta.get_all_inputfields(dct)
        dct = ParserMeta.strip_inputfields_from_dict(input_fields.keys(), dct)
        dct['__parser_args__'] = input_fields
        return super(ParserMeta, cls).__new__(cls, name, parents, dct)

    @staticmethod
    def get_all_inputfields(dct):
        input_fields = {}
        for name, attr in dct.items():
            try:
                assert isinstance(attr, InputField) or issubclass(attr, InputField)
                input_fields[name] = attr
            except (TypeError, AssertionError):
                continue
        return input_fields

    @staticmethod
    def strip_inputfields_from_dict(field_names, dct):
        for name in field_names:
            del(dct[name])
        return dct


class ParserBase(with_metaclass(ParserMeta, reqparse.RequestParser)):
    """ Parser from which all other parsers should inherit from.

    Replaces the standard flask-restful Argument class, with a special
    ErrorHandlingArgument that automatically provides displayable information
    when validation fails.
    """
    def __init__(self, argument_class=ErrorHandlingArgument, **kwargs):
        super(ParserBase, self).__init__(argument_class=argument_class, **kwargs)
        self._set_args()

    def _set_args(self):

        for name, input_field in getattr(self, '__parser_args__').items():

            allowed_args = ['default', 'dest', 'required', 'ignore', 'type',
                            'location', 'choices', 'action', 'help',
                            'operators', 'case_sensitive', 'store_missing']

            actual_args = {k: getattr(input_field, k)
                           for k in vars(input_field)
                           if k in allowed_args}

            self.add_argument(name, **actual_args)


class SqlAlchemyMetaFilterParser(type):
    """ Rewrites any FilterField from the class-level into a special dictionary called __fields__.
    """
    def __new__(mcs, name, parents, attributes):

        filter_fields = SqlAlchemyMetaFilterParser.pop_filter_attributes(attributes)

        instance = super(SqlAlchemyMetaFilterParser, mcs).__new__(mcs, name, parents, attributes)
        setattr(instance, '__fields__', filter_fields)

        return instance

    @staticmethod
    def pop_filter_attributes(attributes):

        filter_fields = {
            attr: val for attr, val in attributes.items()
            if isinstance(val, FilterField)
        }

        # remove attributes from the calss that were moved into __fields__
        for attr in filter_fields:
            del attributes[attr]

        return filter_fields


FIELD_FILTER_MAPPING = {
    sa.Boolean: BooleanFilter,
    sa.DateTime: DateTimeFilter,
    sa.Integer: IntegerFilter,
    sa.String: StringFilter,
    sa.DECIMAL: DecimalFilter,
    pg.ENUM: StringFilter,
    sa.Text: StringFilter,
}

class SqlAlchemyFilterParser(with_metaclass(SqlAlchemyMetaFilterParser, object)):
    """ Parses the query string of the incoming, and generates a servies of SQLAlchemy binary expression objects
    (which are suitable for passing directly to the filter method of a SqlAlchemy BaseQuery object).

    The __model__ attribute MUST be defined at the class-level, as one of your SqlAlchemy model types.
    """
    __model__ = None
    __fields__ = {}

    def __new__(cls, *args, **kwargs):
        if not cls.__model__:
            raise ValueError("__model__ attribute cannot be None.")

        for attr, value in vars(cls.__model__).items():
            # skip if we've already manually defined
            if attr in cls.__fields__:
                continue
            elif not isinstance(value, InstrumentedAttribute):
                # not from the ORM
                continue
            elif not hasattr(value.property, 'columns'):
                # from the ORM, but it's not a column type.. so we skip
                continue

            try:
                cls.__fields__.update({attr: FIELD_FILTER_MAPPING[type(value.property.columns[0].type)]()})
            except KeyError:
                pass

        return super(SqlAlchemyFilterParser, cls).__new__(cls, *args, **kwargs)

    def parse_args(self, req=None):
        """ Returns a set of SqlAlchemy Binary expression objects, based on the input arguments of the current request.

        :param `flask.Request` req: A Flask Request object
        :return: A list of SqlAlchemy BinaryExpression objects.
        :rtype: dict
        """
        if req is None:
            req = request
        source = req.args

        filter_expressions = []

        # loop over every argument that we've defined
        for name, field in iter(self.__fields__.items()):

            for operator in iter(field.operators):

                lookup_key = "{}{op.separator}{op.input_suffix}".format(name, op=operator)

                if lookup_key in source:
                    if operator.rvalue_is_list:
                        # handles multiarg
                        if field.multi_format == 'multiarg':
                            val = source.getlist(lookup_key, type=field.type)
                        elif field.multi_format == 'csv':
                            val = source.get(lookup_key, type=lambda x: [field.type(v) for v in x.split(',')])
                        else:
                            raise ValueError("Unknown fieldspec: {}")
                    else:
                        val = source.get(lookup_key, type=field.type)

                elif operator is field.default_operator and name in source:
                    if operator.rvalue_is_list:
                        # handles multiarg
                        if field.multi_format == 'multiarg':
                            val = source.getlist(name, type=field.type)
                        elif field.multi_format == 'csv':
                            val = source.get(name, type=lambda x: [field.type(v) for v in x.split(',')])
                        else:
                            raise ValueError("Unknown fieldspec: {}")
                    else:
                        val = source.get(name, type=field.type)
                else:
                    continue


                # allow for the attribute to be mapped to something else on dest
                sa_attr = getattr(self.__model__, field.dest or name)
                sa_method = getattr(sa_attr, operator.method_name)
                sa_expression = sa_method(val)

                filter_expressions.append(sa_expression)

        # parse_args returns a dictionary.. even though
        # we're not interested, we always need to return this
        # with a key of 'filters'
        return {'filters': filter_expressions}
