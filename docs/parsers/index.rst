Parsers
=======

Parsers are used to take data from the incoming HTTP request, and convert
those objects into Python objects, to be used in later processing (either
placing them into the database, or building a set of SQL alchemy expressions
for retrieving a subset of data form the database and turning that into a list).

Parsers are also the first step of our data validation process, before making
changes to the underlying data store.

.. warning::
    Instead of polluting your SqlAlchemy data models with validation logic,
    let SqlAlchemy do it's job -- validate whether the data is valid for the
    underlying data store.

Contents:

.. toctree::
    :maxdepth: 2

    general-concepts
    list-parsers
    standard-parsers
    converters
