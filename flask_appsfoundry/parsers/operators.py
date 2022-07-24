from __future__ import absolute_import, unicode_literals

class OperatorBase(object):
    method_name = None
    input_suffix = None
    separator = '__'
    rvalue_is_list = None

    @classmethod
    def generate_expression(cls, sa_model_column, rvalue):
        method = getattr(sa_model_column, cls.method_name)
        expr = method(rvalue)
        return expr


class EqualTo(OperatorBase):
    method_name = "__eq__"
    input_suffix = "eq"


class NotEqualTo(OperatorBase):
    method_name = "__ne__"
    input_suffix = "ne"


class LessThan(OperatorBase):
    method_name = "__lt__"
    input_suffix = "lt"


class GreaterThan(OperatorBase):
    method_name = "__gt__"
    input_suffix = "gt"


class LessThanOrEqual(OperatorBase):
    method_name = "__le__"
    input_suffix = "lte"


class GreaterThanOrEqual(OperatorBase):
    method_name = "__ge__"
    input_suffix = "gte"


class InCollection(OperatorBase):
    method_name = "in_"
    input_suffix = "in"
    rvalue_is_list = True


class NotInCollection(OperatorBase):
    method_name = "notin_"
    input_suffix = "notin"
    rvalue_is_list = True


class Contains(OperatorBase):
    method_name = "contains"
    input_suffix = "contains"
    rvalue_is_list = True


class CaseInsensitiveLike(OperatorBase):
    method_name = "ilike"
    input_suffix = "ilike"


class CaseSensitiveLike(OperatorBase):
    method_name = "like"
    input_suffix = "like"


# COLLECTION_OPERATORS = {
#     'contains': 'contains',
#     'in': 'in_',
#     'notin': 'notin_',
