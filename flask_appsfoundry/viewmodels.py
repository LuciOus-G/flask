"""
Viewmodels
==========

A viewmodel is the representation of your data that will be used to create
your view. (in our case, this is generally JSON data)

In many cases, this will be very similar to an SQLAlchemy model (so this
module defines some reasonable default viewmodels that can be dropped
directly in with no additional subclassing required, in many cases).
"""
from __future__ import absolute_import, unicode_literals

from six import string_types
from sqlalchemy.orm.attributes import InstrumentedAttribute


class SaViewmodelBase(object):
    """ Base class for any viewmodels that present a SQLALchemy model.

    This class is not abstract, and can be instantiated directly.  When
    instantiated, it will iterate over all the properties of a model, and
    copy those same attribute onto itself.

    NOTE: This doesn't work for relation properties -- those will need to be
    defined explicitly in a derived class.
    """
    def __init__(self, model_instance, href_property='api_url'):
        """
        :param model_instance: A SQLAlchemy model instance that this viewmodel
            will ultimately represent.
        :param `string_types` href_property: The name (if present) of the attribute's href property.   This allows
            hrefs (which are generally defined as readonly properties) can be included in the viewmodel as well.
        """
        self._model_instance = model_instance
        self.__href_property = href_property

        for name in self.get_attributes_to_proxy():
            setattr(self, name, getattr(self._model_instance, name))

    def get_attributes_to_proxy(self):
        """ Returns the names of all attributes that will be proxied.

        :return: A list of the names of the attributes in the underlying
            _model_instance that are of InstrumentedAttributes.
        :rtype: `list` of `str`
        """
        want_proxy_attrs = []
        for name, attr in vars(self._model_instance.__class__).items():
            if hasattr(self, name):
                continue
            try:
                if isinstance(attr, InstrumentedAttribute) or name == self.__href_property:
                    want_proxy_attrs.append(name)
            except TypeError:
                pass
        return want_proxy_attrs


class SaListViewmodelBase(object):
    """ Base class for all viewmodels that return a list.

    The list is assumed to be generated from SQLAlchemy models.  **NOTE**:
    This is not an abstract class and can be instantiated directly.
    """
    def __init__(self, query_set, element_viewmodel, *args, **kwargs):
        """
        :param `sqlalchemy.orm.query.Query` query_set: A query that will be
            executed to populate this viewmodel.
        :param `SaViewmodelBase` element_viewmodel: A viewmodel that will be
            used when rendering the individual entities in this viewmodel.
        """
        # NOTE:  *args and **kwargs are just here to swallow any extra params
        self._current_query = query_set
        self._element_viewmodel = element_viewmodel

        # This is used to ultimately hold the data for the results property
        # so that multiple calls to results won't have to rerun the query
        # or regenerate the individual entity viewmodels.
        self.__results__ = None

    @property
    def results(self):
        """ The individual viewmodels that make up our list.

        When called for the first time, whatever query has been
        passed/constructed by this viewmodel will be executed. It's results
        will be iterated over and and individual viewmodel will be
        generated for each entity returned.

        :return: A list of viewmodels, constructed from executing the
            current query.
        :rtype: list (of `SaViewmodelBase` objects)
        """
        try:
            if self.__results__ is None:
                self.__results__ = [
                    self._element_viewmodel(result) for result
                    in self._current_query.all()
                ]
            return self.__results__
        except Exception as e:
            # TODO: implement some clever error handling.
            # This is not clever.
            pass


class OrderedSaListViewmodel(SaListViewmodelBase):
    """ A list viewmodel which can order it's queryset.

    A list viewmodel that allows ordering of the query_set parameter
    by an arbitrary number of ordering arguments.
    """
    def __init__(self, query_set, element_viewmodel, ordering, *args, **kwargs):
        """
        :param `iterable` ordering: A list of expressions which will be passed
            to the query_set's .order_by() method, in the order they are
            returned from the iterable.
        """
        super(OrderedSaListViewmodel, self).__init__(
            query_set,
            element_viewmodel,
            *args, **kwargs)

        for column_ordering in ordering:
            self._current_query = self._current_query.order_by(column_ordering)


class FilteredSaListViewmodel(SaListViewmodelBase):
    """ A list viewmodel that can filter its results.

    When this classis instantiated, it's query_set has it's filtering
    applied to it.
    """
    def __init__(self, query_set, element_viewmodel, filtering, *args, **kwargs):
        """
        :param `iterable` filtering: A list of expressions that will be passed
            to the query_set's .filter() method, in the order which they
            are returned from this iterable.
        """
        super(FilteredSaListViewmodel, self).__init__(
            query_set,
            element_viewmodel,
            *args, **kwargs)

        for filter in filtering:
            self._current_query = self._current_query.filter(filter)


class PaginatedSaListViewmodel(SaListViewmodelBase):
    """ A list viewmodel that can paginate its results.

    To provide pagination information, an extra attribute named
    'metadata' is added which contains information about the result set and
    the pagination applied to it.
    """
    def __init__(self, query_set, element_viewmodel, limit, offset, *args, **kwargs):
        """
        :param int limit: The maximum number of results to include.
        :param int offset: The number of elements to skip from the beginning
            of the result set.
        """
        super(PaginatedSaListViewmodel, self).__init__(
            query_set,
            element_viewmodel,
            *args, **kwargs)

        # metadata MUST be fetched before pagination is applied to query_set
        # otherwise 'count' will be incorrect.
        self.metadata = {
            'resultset': {
                'limit': limit,
                'offset': offset,
                'count': self._current_query.count()
            }
        }

        self._current_query = self._current_query\
                                  .offset(offset)\
                                  .limit(limit)


class ListViewmodel(PaginatedSaListViewmodel,
                    OrderedSaListViewmodel,
                    FilteredSaListViewmodel):
    """ A combination paginated, ordered, and filtered list viewmodel.
    """
    # The ordering of the inherited classes is important!!
    # Pagination logic must run AFTER ordering and filtering.
    pass

