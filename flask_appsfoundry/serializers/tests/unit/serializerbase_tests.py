import unittest

from flask_appsfoundry.serializers import SerializerBase
from flask.ext.restful import fields


class ParentSer(SerializerBase):
    a = fields.String


class ChildSer(ParentSer):
    b = fields.Integer()


class SerializerBaseTests(unittest.TestCase):

    def test_items_method(self):
        ser = ChildSer()
        self.assertEqual(len(ser.items()), 2)

    def test_get_item(self):
        ser = ChildSer()
        self.assertTrue(issubclass(ser.__serializer_fields__['a'], fields.String))
        self.assertTrue(isinstance(ser.__serializer_fields__['b'], fields.Integer))

    def test_set_item(self):
        ser = ChildSer()
        ser.__serializer_fields__['c'] = fields.Float
        self.assertEqual(len(ser.items()), 3)
        self.assertTrue(issubclass(ser.__serializer_fields__['c'], fields.Float))

    # TODO: add expand field test.
