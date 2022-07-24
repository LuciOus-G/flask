import unittest

from flask_appsfoundry.serializers import PaginatedSerializer
from flask.ext.restful import fields


class ParentSer(PaginatedSerializer):
    a = fields.String

class ChildSer(ParentSer):
    b = fields.Integer()


# class SerializerBaseTests(unittest.TestCase):
#
#     def test_items_method(self):
#         ser = ChildSer()
#         results = ser.items()
#         self.assertEqual(len(results), 3)
#

