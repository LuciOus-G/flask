import unittest
from mock import patch
from werkzeug.exceptions import BadRequest
from flask.ext.appsfoundry.parsers.arguments import ErrorHandlingArgument

class ErrorHandlingArgumentTests(unittest.TestCase):

    @patch('flask.ext.appsfoundry.parsers.arguments.restful.abort')
    def test_validation_error_with_description(self, abort):

        error = BadRequest(description="Oops")
        arg = ErrorHandlingArgument("my_arg", error)
        user_message = "{name} is invalid.  {arg_spec}".format(
            name=arg.name,
            arg_spec=arg._stringify_arg_spec()
        ).strip()

        arg.handle_validation_error(error)

        abort.assert_called_once_with(400,
                                      user_message=user_message,
                                      developer_message=error.description)

    @patch('flask.ext.appsfoundry.parsers.arguments.restful.abort')
    def test_validation_error_with_description(self, abort):

        error = Exception("Oops")
        arg = ErrorHandlingArgument("my_arg", error)
        user_message = "{name} is invalid.  {arg_spec}".format(
            name=arg.name,
            arg_spec=arg._stringify_arg_spec()
        ).strip()

        arg.handle_validation_error(error)

        abort.assert_called_once_with(400,
                                      user_message=user_message,
                                      developer_message="Oops")

    def test_stringify_argspec(self):

        arg = ErrorHandlingArgument("id",
                                    required=True,
                                    choices=('a', 'b', 'c', ),
                                    help="Some extra help")

        result = arg._stringify_arg_spec()

        self.assertRegexpMatches(result, r"Required;?")
        self.assertRegexpMatches(result, r"Valid choices: a, b, c;?")
        self.assertRegexpMatches(result, r"Some extra help;?")
