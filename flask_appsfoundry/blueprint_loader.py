"""
Blueprint Loader
================

This is a simple conventions-based module that will return a list of all
module-level variables (recursively through whichever package you specify)
that appear to be blueprints (based on their name alone)

.. warning::
    Remember, this module does NOT inspect it's returned values.  By default,
    it will just look for all subpackages of the package you specify, find all
    modules named blueprints.py, and then return all of their attributes named
    'blueprint' or 'someprefix_blueprint'.

.. note::
    A massive improvement here would be to test the values returned
    from 'discover blueprints', and actually determine if those values are
    indeed blueprints.

.. note::
    Another improvement would be to NOT autoload the
    blueprinty-looking modules on construction.  They should be loaded only
    by the 'discover' method.
"""
from __future__ import absolute_import, unicode_literals
import pkgutil
import re
import importlib
import sys
from traceback import print_tb


class BlueprintLoader(object):
    """
    Simple automatic conventions blueprint loader.
    """
    def __init__(self, app_package, blueprint_module_name='blueprints', import_error_callback=None):
        """
        :param package app_package: Python package which blueprint modules
            will be recursively searched within.
        :param str blueprint_module_name: String name of the blueprints modules
            that we're searching for (without the .py extension)
        """
        regex = re.compile(r'{0}$'.format(blueprint_module_name))

        # walk packages returns a tuple.. so just so I remember which indexes
        (module_loader, name, ispkg) = 0, 1, 2

        packages = pkgutil.walk_packages(
            app_package.__path__,
            "{0}.".format(app_package.__name__),
            onerror=import_error_callback or self.handle_import_error)

        module_names = [pkg[name] for pkg
                        in packages
                        if regex.search(pkg[name])]

        self.blueprint_modules = [importlib.import_module(mod_name)
                                  for mod_name in module_names]

    def discover_blueprints_by_pattern(self, pattern=r'^(.+_)?blueprint$'):
        """
        Searches all the discovered blueprint modules for module-level
        attributes named 'blueprint' or '\*_blueprint' and returns all those
        objects as a list.  This makes no checks if the discovered attributes
        are actually blueprints or not.

        :param regex pattern: Blueprint naming convention.
        :return: A list of (hopefully) blueprint objects.
        """
        regex = re.compile(pattern)

        blueprints = []

        # iterate our blueprint modules, and find attributes matching the
        # provided pattern.
        for bp_module in self.blueprint_modules:
            bp_names = [attr for attr in dir(bp_module) if regex.search(attr)]
            blueprints.extend([getattr(bp_module, bp_name) for bp_name in bp_names])

        return blueprints

    def handle_import_error(self, name):
        """
        Callback function for :py:meth:`pkgutil.walk_packages`, when an import
        error is encountered.

        :param str name: Name of the module that raised an import error.
        """
        (_type, _value_, _traceback) = sys.exc_info()
        print_tb(_traceback)
        raise ImportError("Error importing module {0}".format(name))
