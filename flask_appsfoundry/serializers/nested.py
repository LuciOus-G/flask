"""
Serializers defined here are not intended to be used as stand-alone,
or used for a single field.  Instead they define serializers for common
data that is nested within other objects.

See:
- http://flask-restful.readthedocs.org/en/latest/fields.html#complex-structures
"""
from __future__ import absolute_import, unicode_literals
from flask_restful import fields

from flask_appsfoundry.serializers import SerializerBase

__all__ = ('AddressSerializer', )

# TODO: check if there is anything currently using this.. if not, kill.

class AddressSerializer(SerializerBase):
    """
    Serializer for simple address objects that are not defined with a primary
    key in the database.  This is intended to be used as a nested field.
    """
    def __init__(self):
        self.address1 = fields.String
        self.address2 = fields.String
        self.city = fields.String
        self.province = fields.String
        self.postal_code = fields.String
        self.country_code = fields.String
