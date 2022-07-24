import unittest

from faker import Factory
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from flask.ext.appsfoundry.viewmodels import SaViewmodelBase


fake = Factory.create()


class SaViewmodelBaseTests(unittest.TestCase):

    def setUp(self):

        class Employee(declarative_base()):
            __tablename__ = 'employee'
            id = Column(Integer, primary_key=True)
            first_name = Column(String)
            last_name = Column(String)
            non_model_attr = "Something"

            def some_method(self):
                return fake.pylist()

        self.model = Employee(
            id=fake.pyint(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            non_model_attr=fake.word())

        self.viewmodel = SaViewmodelBase(model_instance=self.model)

    def test_expected_attributes(self):
        self.assertEquals(self.viewmodel.id,
                          self.model.id)

        self.assertEquals(self.viewmodel.first_name,
                          self.model.first_name)

        self.assertEquals(self.viewmodel.last_name,
                          self.model.last_name)

    def test_methods_not_automatically_proxied(self):
        self.assertFalse(hasattr(self.viewmodel, 'some_method'))

    def test_non_model_attributes_not_proxied(self):
        self.assertFalse(hasattr(self.viewmodel, 'non_model_attr'))
