Introduction
============

AppsFoundry's internal-use Flask-extension library encapsulating common
functionality for building API endpoints, data models, serializing outgoing
data, parsing incoming data, semi-automagically build proxy classes for rending
output, handling API errors in a standard way, auto-discovering api blueprints,
and a few other helpful things.

This library assumes use with Flask, SQLAlchemy, and has many features built
on top of Flask-RESTFul.

.. note:: Right off the bat, remember, this is a Flask extension package,
    so although these packages are in a base package called
    **flask_appsfoundry**, that will be rewritten by flask to
    **flask.ext.appsfoundry**.  Flask wants you to import extensions under
    the ext namespace, but either import works.

Contents:

.. toctree::
   :maxdepth: 2

   quickstart
   blueprint_loader
   httpstatus
   auth/index
   models
   parsers/index
   controllers/index


Outstanding Issues
==================

* Our error response codes need clarified, migrated into this package, and
    renamed something sane.
* 400, 401, 404 responses all need our internal error codes checked and
    verified.
* Parser classes don't support inheritance of their parser fields.  They
    also do not support arbitrarily-nested fields (directly).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
