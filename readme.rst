flask_appfoundry (Scoop Flask)
==============================

Common utilities and base classes for all Apps Foundry projects based on Flask
and/or SQL Alchemy.

Build Status
------------

+-------+---------------------------------------------------------------------------------------------+
| Tests | .. image:: http://ci.apps-foundry.com/buildStatus/icon?job=scoopcor-update-pypi             |
+-------+---------------------------------------------------------------------------------------------+
| Build | .. image:: http://ci.apps-foundry.com/buildStatus/icon?job=scoopflask-py27-pypi-builder     |
+-------+---------------------------------------------------------------------------------------------+
| Docs  | .. image:: http://ci.apps-foundry.com/buildStatus/icon?job=scoopflask-docs-builder          |
+-------+---------------------------------------------------------------------------------------------+

Features
--------

* Blueprint Discovery
* SQLAlchemy Mixins
* API controller support base classes and mixins:
    * controllers
    * input parsers
    * response field serializers
    * viewmodels (proxy classes)


.. code-block:: python

    from flask import route, request
    from flask_appsfoundry.parsers import FilterOptionsParserBase
    from flask_appsfoundry import filterinputs as field
    from . import models

    class BannerListParser(FilterOptionsParserBase):

        __model__ = models.Banner

        id = field.Integer()
        name = field.String()
        is_active = field.Boolean()
        clients = field.IntegerList()
        display_from = fields.DateTime('iso8601')


    @route('/some-url')
    def handle_request():
        parser = BannerListParser()
        expressions = parser.parse_args(request)



Running Tests
-------------

This project uses nose as it's testing framework.

**NOTE:** For running functional tests, you will need an empty PostgreSQL database
available, which you have superuser privileges to.

Additionally, for the functional tests to run, you'll need an empty PostgreSQL
database, which you have superuser privileges to.  The SQLAlchemy database uri
must be set as the environmental variable TEST_DATABASE.  Something like this:

.. code-block:: bash

    FEA_TEST_DATABASE=postgresql://postgres@localhost/scoopflask_testdb

**PROTIP:** Do this in your IDE as part of your test run configuration.


Environmental Variables
-----------------------

All are prefixed with 'FEA_' (think flask extension appsfoundry).

* FEA_TEST_DATABASE - A sqlalchemy database uri that will be used by the
    functional tests to make sure that we're working properly.


Additional Resources
--------------------

* `Full Documentation <https://google.com/>`_

