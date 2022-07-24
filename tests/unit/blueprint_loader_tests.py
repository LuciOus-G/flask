import unittest

from flask_appsfoundry.blueprint_loader import BlueprintLoader

from tests.fixtures import blueprint_loader as app


class LoadByPatternTests(unittest.TestCase):
    """ Tests

    """
    def test_finds_blueprint_modules(self):

        bpl = BlueprintLoader(app)

        expected_modules = ['tests.fixtures.blueprint_loader.aduh.blueprints',
                            'tests.fixtures.blueprint_loader.meh.blueprints',
                            ]

        actual_modules = [bp_module.__name__ for bp_module in bpl.blueprint_modules]

        for expected in expected_modules:
            self.assertIn(expected, actual_modules)

    def test_blueprint_attributes(self):

        bpl = BlueprintLoader(app)

        expected = 3

        actual = len(bpl.discover_blueprints_by_pattern())

        self.assertEqual(actual, expected)
