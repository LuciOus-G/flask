from __future__ import absolute_import, unicode_literals
from .converters import sqlalchemy_orderby_statement
from .parsers import ParserBase
from .standardinputs import CSVField, PositiveIntegerField, NaturalNumberField, InputField

__all__ = ['PaginationParser', 'SqlAlchemyOrderingParser', 'FieldLimitingParser', 'FieldExpandingParser', ]

class PaginationParser(ParserBase):
    """
    Retrieves common pagination options from the request.
    """
    limit = PositiveIntegerField(default=20)
    offset = NaturalNumberField(default=0)


class SqlAlchemyOrderingParser(ParserBase):
    order = InputField(type=sqlalchemy_orderby_statement, action='append', default=[])


class FieldLimitingParser(ParserBase):
    fields = CSVField(default=['all', ])


class FieldExpandingParser(ParserBase):
    expand = CSVField(default=[])

