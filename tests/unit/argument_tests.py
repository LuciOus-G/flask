import unittest

from flask_restful import reqparse, inputs

from flask.ext.appsfoundry.parsers.arguments import ErrorHandlingArgument


class ErrorHandlingArgumentTests(unittest.TestCase):

    def required_in_argspec(self):

        parser = reqparse.RequestParser(argument_class=ErrorHandlingArgument)
        parser.add_argument('abc', type=inputs.boolean, required=True)



