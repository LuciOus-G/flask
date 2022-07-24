Essential Concepts
==================

There are 5 essential parts to our API architecture.

1. Controllers
    Controllers perform the same role they do in any application.
    It is highly preferable to not HIDE the logic of your controllers, when
    they are written from scratch, but remember you want to show 'big picture'
    what is happening.  Don't show too many details, and don't show too few
    details (encapsulating all of your controller's logic into a single
    method call hurts readability enormously).
2. Data Models
    Usually just called 'models', these are your SQLAlchemy classes that you
    use to interact with the database.  We're using SQLAlchemy, so remember,
    although this is your primary tool for interacting with the database, it
    is not your only tool!
3. Viewmodels
    A modified representation of your 'Data Model' that will be rendered into
    JSON.  This is not the full story of how these work though -- we actually
    use a 2-part viewmodel system.  Our viewmodels are proxy classes of our
    data models and do not need to expose only string attributes -- the
    attributes of these classes can be anything, including complext data-types
    that cannot be directly rendered as strings.  These are used in conjunction
    with a serializer to render the final form of the viewmodel.
4. Serializers
    Used to describe how the attributes of a viewmodel are rendered into
    strings (for inclusion in a final viewmodel model).  Generally our outgoing
    data is JSON, so this will render them exactly.
5. Parsers
    Turns the incoming request into python data types.

.. code-block::

    Request Flow
    ------------
        http request
            |
            |
            V
        controller
            |
            |
            V
          parser


