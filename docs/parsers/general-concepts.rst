General Parser Concepts
=======================

Our parsing framework is based on top of Flask-Restful's RequestParser.
The API for creating a parser is similar, to RequestParser, although the
way parsers are defined is much different.

Standard parsers are build directly on top of RequestParser, whereas
List (Filter) parsers only share a similar API, but the parsing internals
have been completely stripped and replaced.

Standard parsers are used generally for POST/PUT (create/update) commands,
whereas List (Filter) parsers are generally only used for GET methods.
