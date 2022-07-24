List (Filter) Parsers
=====================

These parsers are unique.  Instead of returning python objects representing
the request, they are tied directly to an individual sql alchemy model.

They read the request arguments (usually from the query string), and then
turn those into SqlAlchemy binary expression objects, which are suitable
for passing to the .filter() method of a base query.

Example Usage
-------------

.. code-block:: python

    from . import models, choices
    from flask.ext.appsfoundry.parsers import (
        SqlAlchemyFilterParser, IntegerFilter, EnumFilter, StringFilter,
        BooleanFilter, DateTimeFilter)

    class MyBannerParser(SqlAlchemyFilterParser):

        __model__ = models.MyBanner

        id = IntegerFilter()
        banner_type = EnumFilter(enum=choices.ACTIONS)
        name = StringFilter()
        is_active = BooleanFilter()
        created = DateTimeFilter()
        client_id = IntegerFilter(dest='clients', default_operator='contains')

    # then, inside of some controller or flask endpoint
    def do_stuffs():
        parser = MyBannerParser()

        query = models.MyBanner.query
        for expr in parser.parse_args():
            query = query.filter(expr)

        results = query.all()

.. autoclass:: flask_appsfoundry.parsers.parsers.SqlAlchemyFilterParser
    :members:
    :show-inheritance:

The Filter Parser
-----------------

.. automodule:: flask_appsfoundry.parsers.filterinputs
    :members:
    :show-inheritance:
