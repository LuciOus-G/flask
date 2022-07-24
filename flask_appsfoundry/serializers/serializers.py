from __future__ import absolute_import, unicode_literals
from . import fields

__all__ = ('SerializerBase', 'PaginatedSerializer', )

class SerializerBase(dict):
    """
    Base class that all class-based serializers should inherit from.

    See :meth`items` for notes related to the current implementation.
    """
    def __init__(self):
        self.__deleted_attributes__ = []
        super(SerializerBase, self).__init__()

    def __new__(cls, *args, **kwargs):

        inst = super(SerializerBase, cls).__new__(cls, *args, **kwargs)
        inst.__serializer_fields__ = {}

        for attr in dir(inst):
            val = getattr(inst, attr)
            try:
                assert isinstance(val, fields.Raw) or issubclass(val, fields.Raw)
                inst.__serializer_fields__[attr] = val
            except (AssertionError, TypeError):
                continue

        inst.items = lambda: {k: inst.__serializer_fields__[k]
                              for k in inst.__serializer_fields__}.items()

        return inst

    def __delattr__(self, item):
        del self.__serializer_fields__[item]

    def add_expand_field(self, name, inner_serializer):
        self.__serializer_fields__[name] = inner_serializer


class PaginatedSerializer(SerializerBase):
    """
    Defines the serialization format for a paginated result set.
    See: :py:class:`app.commmon.viewmodels.PaginatedSaListViewmodel`
    """
    def __init__(self, set_serializer, set_name):
        super(PaginatedSerializer, self).__init__()

        self.__serializer_fields__[set_name] = \
                fields.List(fields.Nested(set_serializer), attribute='results')

        self.__serializer_fields__['metadata'] = fields.Nested({
            'resultset': fields.Nested({
                "count": fields.Integer,
                "limit": fields.Integer,
                "offset": fields.Integer,
            })
        })

