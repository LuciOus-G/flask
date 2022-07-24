import unittest

from faker import Factory
import sqlalchemy as sa

from flask_appsfoundry.parsers import operators

fake = Factory.create()


class BaseOperatorTests(unittest.TestCase):

    def test_generate_expression_left(self):

        op = operators.OperatorBase()
        setattr(type(op), 'method_name', '__eq__')

        col = sa.Column(fake.word(), sa.Integer())

        rval = fake.pyint()

        expr = op.generate_expression(col, rval)

        self.assertIs(col, expr.left)

    def test_generate_expression_right(self):

        op = operators.OperatorBase()
        setattr(type(op), 'method_name', '__eq__')

        col = sa.Column(fake.word(), sa.Integer())

        rval = fake.pyint()

        expr = op.generate_expression(col, rval)

        self.assertEqual(rval, expr.right.value)
        self.assertIsInstance(expr.right.type, sa.Integer)


class EqualsOperatorTests(unittest.TestCase):

    def test_generate_expression_left(self):

        op = operators.EqualTo()

        col = sa.Column(fake.word(), sa.Integer())

        rval = fake.pyint()

        expr = op.generate_expression(col, rval)

        self.assertIs(col, expr.left)

    def test_generate_expression_right(self):

        op = operators.EqualTo()

        col = sa.Column(fake.word(), sa.Integer())

        rval = fake.pyint()

        expr = op.generate_expression(col, rval)

        self.assertEqual(rval, expr.right.value)
        self.assertIsInstance(expr.right.type, sa.Integer)
