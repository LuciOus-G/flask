"""
Flask-AppsFoundry
=================

This package is a declarative API framework, based in some part, on top of
Flask-RESTful.
"""
# import gettext
# import os
__version__ = '0.1.32'


try:
    from flask_restful import *
except ImportError:
    # This can throw errors on install when checking the version before
    # dependencies are installed
    pass

# gettext.install('scoop_flask', os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'translations')))
