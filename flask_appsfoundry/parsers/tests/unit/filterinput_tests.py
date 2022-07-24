import unittest
from flask_appsfoundry.parsers.filterinputs import FilterField
from flask_appsfoundry.parsers.operators import EqualTo, NotEqualTo
import inspect
import warnings

# NOTE: the other operators here don't implement any logic, and as
#   such get their test coverage elsewhere.


class FilterFieldTestCase(unittest.TestCase):

    def test_default_operator(self):
        ff = FilterField()

        if inspect.isclass(ff.default_operator):
            self.assertTrue(issubclass(ff.default_operator, EqualTo))
        else:
            self.assertIsInstance(ff.default_operator, EqualTo)

    def test_explicit_default_operator(self):
        ff = FilterField(default_operator='ne')

        if inspect.isclass(ff.default_operator):
            self.assertTrue(issubclass(ff.default_operator, NotEqualTo))
        else:
            self.assertIsInstance(ff.default_operator, NotEqualTo)

    def test_warn_unsupported_args(self):
        # explicitally unsupported args from that ARE supported by
        # flask-restful RequestParse
        unsupported_args = ['required',
                            'ignore',
                            'action',
                            'operators',
                            'store_missing']

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            for arg in unsupported_args:
                self.assertRaises(UserWarning,
                                  lambda: FilterField(**{arg: "Something"}))

