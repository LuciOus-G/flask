Tutorial
========

These modules represent common functionality throughout our Flask-based
applications.  The key word there is **COMMON**.  They're not appropriate
for use in **ALL** modules, but they are definitely appropriate in
**MOST** (80-90% of what our APIs do).

The API portions of this library are built on top of Flask-RESTful.  In many
cases, the features of Flask-RESTful are exposed through this library (ideally,
eventually replacing the need to have Flask-RESTful as both a dependency of
our apps, and this module.)

Key Concepts
------------

In our controller patterns, we have essentially 5 different concepts:

Data Model
    These are your SqlAlchemy ORM model classes.
View Model
    Often closely-related to your SQLAlchemy models (so closely-related
    that the controller classes will automatically generate one of these
    for you, based on your Data Model, if you don't explicitly define one.
Serializer
    An object that defines how each field in the View Model is turned
    from a python object, into a string.
Parser
    The opposite of a Serializer.  Defines how input values are turned into
    python objects.  The parser also plays unfortunate double-duty of also
    defining WHERE it grabs it's input from (query string, body as
    form/multipart, body as application/json, headers, etc..)
Controller
    Exactly what you expect.  They're the same thing as controllers in any
    other MVC web framework.


Input Flow
----------

Let's examine a typical HTTP POST flow (we'll assume that the POST request
is being used to create a new object).

We have a SqlAlchemy model defined called 'Employee'

.. code-block:: python

    # app/employees/models.py
    from app import db
    from flask.ext.appsfoundry.models import SoftDeletableMixin

    class Employee(SoftDeletableMixin, db.Base):
        first_name = db.Column(db.String(50), nullable=False)
        last_name = db.Column(db.String(50), nullable=False)
        hire_date = db.Column(db.DateTime(), nullable=False)

Ok, now that we've got a class we can use to persist the user's input
(our data model) we need a class to read in the User Agent's input from the
HTTP Request, we're going to need a 'Parser', that inherits from 'ParserBase'.

Note, this simple input parser is actually based on type of Flask-RESTful's
RequestParser class, and takes all the same arguments as RequestParsers's
.add_argument() method.  Check that out for all the supported arguments and
what they do.

.. code-block:: python

    # app/employees/parsers.py
    from datetime import datetime

    from flask.ext.appsfoundry.parsers import ParserBase, InputField, converters
    from flask.ext.restful.inputs import boolean

    class CreateEmployeeParser(ParserBase):
        first_name = InputField(requied=True)
        last_name = InputField(required=True)
        hire_date = InputField(type=converters.naive_datetime_from_iso8601,
                               default=datetime.now)
        is_active = InputField(type=boolean)

There are a few interesting things going on here.. First, we have more fields
than we defined in our data model, because the Employee data model includes
the SoftDeletableMixin, which id and is_active (we don't define id though,
because that's generated from our database).

Also, you'll note that hire_date includes a default value.  If not included,
it will use the value OR callable assigned to default.  Lastly, type IS NOT
simply a type (unless that type is callable.. which most are).  It takes any
callable (so you can put a simple lambda function here), that takes a single
input parameter (always a unicode string), and returns the appropriate
python datatype.  If no type is defined, a unicode string will be returned.

If a required parameter is missing, or a type conversion fails, then a
werkzeug.exceptions.BadRequest will be raised.  In turn, if not caught by our
code, that will return HTTP 400.

See << ErrorHandlingApi >> for more details on what data is returned in the
response body.

NOTE: by default, parser will read JSON values from a post body if the
content-type is appllication/json, or form/multi-part. Lastly, it will try
to extract values from the query string.  This can be overridden with the
location parameter.

Now, if we were using that code inside of a flask endpoint, we can parse
the input values as such:

.. code-block:: python

    # app/employees/api.py
    from . import parsers

    @app.route('/employees/', methods=['POST'])
    def some_route():
        parser = parsers.EmployeeParserBase()
        args = parser.parse_args()
        # args is now a dictionary
        # that will look something like the following:
        #
        # args = {
        #         'first_name': unicode,
        #         'last_name': unicode,
        #         'hire_date': datetime,
        #         'is_active': bool
        # }
        #
        # further processing here


args is set to a dictionary, containing 4 keys
first_name, a unicode string.  last_name, a unicode string.  hire_date as a
python datetime with no timezone.  is_active as python bool.

Now, that's great.  Let's say we want to use our post data persist our
Employee object to the database.

.. code-block:: python

    # app/employees/api.py
    from . import parsers, models
    from app import db

    @app.route('/employees/', methods=['POST'])
    def some_route():
        # parse our input
        parser = parsers.EmployeeParserBase()
        args = parser.parse_args()

        # create an employee object
        emp = models.Employee(**args)

        # add to the session, and submit to the database
        session = models.Employee.session
        session.add(emp)
        session.commit()

Finally, we'd like to return a serialized representation of the new employee
object we just created, with the HTTP Status Code 201.

To do this, we need to create a serializer, which will turn the fields in our
model, into string values that can be properly sent out as a response.  For
this, we're going to create a serializer, and then leverage a feature of the
underlying Flask-RESTful library--namely, marshalling.

.. code-block:: python

    # app/employees.serializers
    from flask.ext.appsfoundry import serializers
    from flask.ext.appsfoundry.parsers import fields

    class EmployeeSerializer(serializers.SerializerBase):
        id = fields.Integer
        first_name = fields.String
        last_name = fields.String
        hire_date = fields.DateTime('iso8601)
        is_active = fields.Boolean

.. code-block:: python

    # app/employees/api.py
    from . import parsers, models, serializers
    from flask.ext.appsfoundry import marshal, httpstatus

    @app.route('/employees/', methods=['POST'])
    def some_route():
        # parse our input
        parser = parsers.EmployeeParserBase()
        args = parser.parse_args()

        # create an employee object
        emp = models.Employee(**args)

        # add to the session, and submit to the database
        session = models.Employee.session
        session.add(emp)
        session.commit()

        # create a serializer
        serializer = serializers.EmployeeSerializer())

        return (marshal(emp, serializer), httpstatus.CREATED)




.. code-block:: python

    # app/employees/serializers.py
    from flask.ext.appsfoundry import serializers

    class EmployeeSerializer(serializers.SerializerBase):
