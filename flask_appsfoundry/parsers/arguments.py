"""
Arguments
=========

Arguments are replacements for the default Argument type provided by reqparse.

Unless you KNOW you need to change Argument, you probably don't.
Probably what you're looking for is in filterinputs, standardinputs,
converters, or parsers.

This is a byproduct of Flask-RESTful's very gross reqparser architecture.
It works a little bit like this:

.. code-block:: python

    parser = reqparse.RequestParser(
        argument_class=ArgumentClassGoesHere,
        namespace_class=NamespaceClassGoesHere
    )
    # this creates a new instance of ArgumentClassGoesHere
    parser.add_argument('name')

    # then places the instance in a list called args
    parser.args
    # >> <ArgumentClassGoesHere object at 0x10594e850>]

    results = parser.parse_args()
    print(results)
    # >> {} <-- this is actually an instance of NamespaceClass, which is
    #           expected to act like a dictionary.. it's default implementation
    #           is essentially just a normal dictionary.

"""
from __future__ import absolute_import, unicode_literals
from collections import namedtuple

import flask_restful as restful
from flask_restful import reqparse


class ErrorHandlingArgument(reqparse.Argument):
    """
    Overrides the default error information when Argument validation fails.
    Included in the raised error will be a user_message and developer_message
    in the exception.data dictionary.
    """
    def _stringify_arg_spec(self):
        """
        Gets an english-language string specifying this argument's requirements.

        :return: A string formatted like: "Required; Valid choices: a, b, c; {help-text}"
        """
        specs = [
           "Required" if self.required else None,

           "Valid choices: {0}".format(
               ", ".join("{0}".format(c) for c in self.choices),
           ) if self.choices else None,

           self.help if self.help else None
        ]

        complete_spec = "; ".join(s for s in specs if s is not None)

        return complete_spec

    def handle_validation_error(self, error, *args, **kwargs):
        """
        Override the default handling of validation exceptions.
        If left as default, this method will override any description set on
        our error message.

        We want the 'help message' to be returned as the 'user_message',

        :param error: the error that was raised
        """
        user_msg = "{name} is invalid.  {arg_spec}".format(
            name=self.name,
            arg_spec=self._stringify_arg_spec()
        ).strip()

        dev_msg = getattr(error, 'description', str(error))

        restful.abort(400, user_message=user_msg, developer_message=dev_msg)

    def __str__(self):
        return "<ErrorHandlingArgument (name={name})>".format(name=self.name)

    def __repr__(self):
        attrs_spec = []
        for name, val in vars(self).items():
            attrs_spec.append("{}={}".format(name, str(val)))
        attrs_spec = ", ".join(attrs_spec)
        return "<ErrorHandlingArgument ({})>".format(attrs_spec)


FakeRequest = namedtuple('FakeRequest', ['unparsed_arguments', 'json'])



_friendly_location = {
    u'json': u'the JSON body',
    u'form': u'the post body',
    u'args': u'the query string',
    u'values': u'the post body or the query string',
    u'headers': u'the HTTP headers',
    u'cookies': u'the request\'s cookies',
    u'files': u'an uploaded file',
}

class NestedJsonParserArgument(ErrorHandlingArgument):

    # def source(self, request):
    #     fake_req = FakeRequest(unparsed_arguments=MultiDict(),
    #                            json=request.json.get(self.name))
    #     return fake_req

    def __str__(self):
        return "<NestedJsonParserArgument (name={name})>".format(name=self.name)

    def __repr__(self):
        attrs_spec = []
        for name, val in vars(self).items():
            attrs_spec.append("{}={}".format(name, str(val)))
        attrs_spec = ", ".join(attrs_spec)
        return "<NestedJsonParserArgument ({})>".format(attrs_spec)

    def source(self, request):
        """Pulls values off the request in the provided location
        :param request: The flask request object to parse arguments from
        """
        return request.json.get(self.name, {})

    def parse(self, request):
        """Parses argument value(s) from the request, converting according to
        the argument's type.

        :param request: The flask request object to parse arguments from
        """
        source = self.source(request)

        results = []

        # Sentinels
        _not_found = False
        _found = True

        for operator in self.operators:
            name = self.name + operator.replace("=", "", 1)
            if name in source:
                # Account for MultiDict and regular dict
                if hasattr(source, "getlist"):
                    values = source.getlist(name)
                else:
                    values = [source.get(name)]

                for value in values:
                    if hasattr(value, "lower") and not self.case_sensitive:
                        value = value.lower()

                        if hasattr(self.choices, "__iter__"):
                            self.choices = [choice.lower()
                                            for choice in self.choices]

                    try:
                        value = self.convert(value, operator)
                    except Exception as error:
                        if self.ignore:
                            continue
                        self.handle_validation_error(error)

                    if self.choices and value not in self.choices:
                        self.handle_validation_error(
                            ValueError(u"{0} is not a valid choice".format(
                                value
                            ))
                        )

        if not results and self.required:
            if isinstance(self.location, six.string_types):
                error_msg = u"Missing required parameter in {0}".format(
                    _friendly_location.get(self.location, self.location)
                )
            else:
                friendly_locations = [_friendly_location.get(loc, loc)
                                      for loc in self.location]
                error_msg = u"Missing required parameter in {0}".format(
                    ' or '.join(friendly_locations)
                )
            self.handle_validation_error(ValueError(error_msg))

        if not results:
            if callable(self.default):
                return self.default(), _not_found
            else:
                return self.default, _not_found

        if self.action == 'append':
            return results, _found

        if self.action == 'store' or len(results) == 1:
            return results[0], _found
        return results, _found
