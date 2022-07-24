from flask import Flask

# HACK:  Temporary relative imports to get my test runner happier.


def single_purpose_parser(parser_class, field_under_test, *args, **kwargs):
    '''
    Creates a special purpose parser that will only test a single
    field that we're interested in.  Any furhter arguments, beyond
    the first two will be passed to the parser constructor.

    :param parser_class: The TYPE of a parser class that we're instantiating
    :param field_under_test: The string name of the parser arg we want to test.
    '''
    p = parser_class(*args, **kwargs)

    for parg_name in [parg.name for parg
                      in p.args
                      if parg.name != field_under_test]:
        p.remove_argument(parg_name)

    return p


test_app = Flask(__name__)
