"""
Configuration
=============

Classes that can be used as the configuration object for Flask-based
projects.


**See Also**

- http://flask.pocoo.org/docs/0.10/config/
- https://www.jetbrains.com/pycharm/help/run-debug-configuration-python.html
"""
from __future__ import absolute_import, unicode_literals
import os
from types import ModuleType


class ScoopConfig(object):
    """ Class for configuring Flask from Environmental Variables.

    .. note::

        This class also fully supports our previous convention of using
        a file named local_config.py to override configuration on a
        system-by-system basis, although the preferred method going forward
        is to set environmental variables.

        If you want to load local_config, just make a call to super()
        from your init, LAST, after all your regular variables have been set.
    """

    environment_prefix = ""

    __local_config_loaded = None

    def __init__(self):
        self.import_local_config()

    def _bool(self, varname, default=None):
        """ Fetched the named environmental variable, and returns as a boolean.

        :param `str` varname: Non-prefixed environmental variable name.
        :param `bool` default: Value to return if varname is not defined.
        :return: A boolean representing the environmental variable.
        :rtype: bool
        """
        return self.__env(
            varname=varname,
            default=default,
            type=lambda x: x.lower() in ['1', 'true', 't'],
        )

    def _str(self, varname, default=None):
        """ Fetches the named environmental variable, and returns as a string.

        .. note::

            Environmental variables are always read in as strings, so this
            is really just provided for readability.  It just wraps the
            default actions of __env.

        :param `str` varname: Non-prefixed environmental variable name.
        :param `str` default: Value to return if varname is not defined.
        :return: A string representing the environmental variable.
        :rtype: str
        """
        return self.__env(
            varname=varname,
            default=default,
            type=str
        )

    def _int(self, varname, default=None):
        """ Fetches the named environmental variable, and returns as an integer.

        :param `str` varname: Non-prefixed environmental variable name.
        :param `int` default: Value to return if varname is not defined.
        :return: An int representing the environmental variable.
        :rtype: int
        """
        return self.__env(
            varname=varname,
            default=default,
            type=int
        )

    def __env(self, varname, default=None, type=str):
        """ Fetches an environmental variable and returns it's value as type.

        :param `str` varname: The non-prefixed variable name
        :param `object` default: Value to return if env var is not defined.
        :param `callable` type: A single-parameter function to use to convert
            the environmental variable's value to it's final python type.
        :return: An object representing whatever
        """
        value = os.getenv(self.environment_prefix + varname)

        if value is None:
            return default

        return type(value)

    def import_local_config(self):
        """ If existant, 'local_config' module is loaded all MODULE-LEVEL
        configuration values will be read in and set on this instance of this
        class.

        :return: None -- This method only has side-effects.
        """
        try:
            import local_config
            # iterates all the module-level names which do NOT represent
            # other modules, or appear to be private/protected.
            name_values = [(k, v) for k, v in vars(local_config).items() if
                   not (isinstance(v, ModuleType) or k.startswith("_"))]
            setattr(self, name_values[0], name_values[1])
        except ImportError:
            pass
