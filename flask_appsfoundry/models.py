"""
Models
======

Mixins to support common functional in our SqlAlchemy data models.  These are
mixins, and not full-on base classes, so you still must inherit from some kind
of DeclarativeBase base class from SqlAlchemy in your models.
"""
from __future__ import unicode_literals, absolute_import
from datetime import datetime

import inflect
from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declared_attr


class BaseDatamodelMixin(object):
    """ A model with an integer primary key property, named 'id'

    This class also supports auto-generation of the __tablename__ property, as well as some sane defaults for __repr__.
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        """ Returns a pluralized table name, based on the class name.

        The class name will be lower-cased, pluralized, and prefixed with
        'core_', as is our convention.
        """
        p = inflect.engine()
        plural_name = p.plural_noun(cls.__name__)
        return 'core_{0}'.format(plural_name.lower())

    def __repr__(self):
        """ Unicode string representation of this model

        Contains the model class's name, it's database id, and it's name (if that attribute is present), followed by
        all other attributes.
        ex: <Item (id: 15, name: The Grapes of Wrath, type: book, ...etc..)>
        """
        attrs = vars(self).copy()

        # set the id and name first, if they exist.
        attrs_str = 'id: {}'.format(attrs.pop('id', None))
        if 'name' in attrs:
            attrs_str += ', name: {}'.format(attrs.pop('name'))

        # then set any other properties
        for name, value in attrs.items():
            if name.startswith("_"):
                continue
            attrs_str += ', {}: {}'.format(name, value)

        return attrs_str

    def __str__(self):
        """ Unicode string representation of this model.

        Contains the model class's name, it's database id, and it's name
        (if that attribute is present).
        ex: <Item (id: 15, name: The Grapes of Wrath)>
        """
        if hasattr(self, 'name'):
            return '<{classname} (id: {id}, name: {name})>'.format(
                classname=self.__class__.__name__,
                id=self.id,
                name=self.name)
        else:
            return '<{classname} (id: {id})>'.format(
                classname=self.__class__.__name__,
                id=self.id)


class TimestampMixin(BaseDatamodelMixin):
    """ Model with auto-updating 'created' and 'modified' datetime properties.

    Includes support for automatic updating of these records.  Note: this is done in python, not at the database level.
    """
    created = Column(DateTime,
                     default=datetime.utcnow)
    modified = Column(DateTime,
                      default=datetime.utcnow,
                      onupdate=datetime.utcnow)


class SoftDeletableMixin(BaseDatamodelMixin):
    """ A model with an is_active boolean property.

    Supports our common practice of creating soft-deletable models that have an is_active boolean property that,
    when false, indicates that record has been deleted.
    """
    is_active = Column(Boolean, nullable=False, default=True)


