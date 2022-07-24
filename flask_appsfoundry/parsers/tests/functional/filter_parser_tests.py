from __future__ import unicode_literals, absolute_import
from unittest import TestCase

from flask import Flask
from flask_appsfoundry.parsers import SqlAlchemyFilterParser, StringFilter

from flask_sqlalchemy import SQLAlchemy


test_app = Flask(__name__)

test_app.config.from_object = {
    'SQLALCHEMY_DATABASE_URI': ''
}

test_db = SQLAlchemy(test_app)


class Bule(test_db.Model):
    __tablename__ = 'bules'
    id = test_db.Column(test_db.Integer, primary_key=True)
    name = test_db.Column(test_db.String())
    age = test_db.Column(test_db.Integer())


class BuleFilterParser(SqlAlchemyFilterParser):
    name = StringFilter()
    __model__ = Bule


class FilterParserTests(TestCase):

    def setUp(self):
        # insert data into the database
        test_db.create_all()
        for meh in [{'name': 'derek', 'age': 199}, {'name': 'togi', 'age': 234}]:
            test_db.session().add(Bule(**meh))
        test_db.session.commit()

    def tearDown(self):
        test_db.drop_all()

    def test_explicit_filter_field(self):
        with test_app.test_request_context("/?name=derek") as ctx:
            filters = BuleFilterParser().parse_args(req=ctx.request).pop('filters')
            query = test_db.session().query(Bule)
            for f in filters:
                query = test_db.session().query(Bule).filter(f)

            results = query.all()

            self.assertEquals(len(results), 1)

            self.assertEquals(
                results[0].name, 'derek'
            )
            self.assertEquals(
                results[0].age, 199
            )

    def test_automatic_filter_field(self):
        with test_app.test_request_context("/?age=199") as ctx:
            filters = BuleFilterParser().parse_args(req=ctx.request).pop('filters')
            query = test_db.session().query(Bule)
            for f in filters:
                query = test_db.session().query(Bule).filter(f)

            results = query.all()

            self.assertEquals(len(results), 1)

            self.assertEquals(
                results[0].name, 'derek'
            )
            self.assertEquals(
                results[0].age, 199
            )
