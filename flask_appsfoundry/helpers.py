"""
Helpers
=======

Simple and generic functions or classes that don't really belong in any other
modules or namespaces.  By their nature, everything in here should be
extremely generic and usable in many places and possibly in many different
situations.
"""
from __future__ import absolute_import, unicode_literals


def get_or_create_instance(obj, *args, **kwargs):
    """ Instantiates an object (or directly returns that object if already).

    When the first argument to this method is an instance of an object,
    it will be returned with no further modifiations.  If however, the
    first argument is a class, then it will be instantiated with whichever
    args and kwargs were passed to this method.

    :param obj: Any object instance or class.
    :param args: positional args to be passed to obj's constructor.
    :param kwargs: keyword to be passed to obj's constructor.
    :return: obj, or a new instance of obj.
    """
    return obj(*args, **kwargs) if isinstance(obj, type) else obj
