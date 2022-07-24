import unittest

from flask.ext.appsfoundry.helpers import get_or_create_instance

from mock import MagicMock


class GetOrCreateInstanceTests(unittest.TestCase):

    def test_get_instance(self):
        mm = MagicMock()
        self.assertIs(mm, get_or_create_instance(mm))
        self.assertEqual(mm.call_count, 0)


    def test_class(self):
        mclass = MagicMock
        mm = get_or_create_instance(mclass)
        self.assertIsInstance(mm, mclass)
        self.assertIsNot(mm, mclass)

    def test_class_called_with_expected_args(self):
        class mockclass(object):
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
        mm = get_or_create_instance(mockclass, 1, 2, a=1, b=2)

        self.assertEqual(mm.args, (1,2))
        self.assertEqual(mm.kwargs, {'a':1, 'b':2})
