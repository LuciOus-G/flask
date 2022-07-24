from hashlib import md5

from flask import request, jsonify
from flask_appsfoundry import Resource, marshal, serializers, viewmodels
from flask_appsfoundry.helpers import get_or_create_instance
from flask_appsfoundry.auth.constants import TOKEN_PREFIX
from flask_appsfoundry.auth.helpers import assert_user_has_any_permission
from flask_appsfoundry.controllers.base import DbSetApiMixin
from flask_appsfoundry.parsers import specialized
from six.moves.http_client import OK, CREATED, NO_CONTENT

class ScoopAuthMixin(object):
    """ This mixin performes the authorization and authentication logic against
    ScoopCAS.  This is really a horrible hack and should live in the individual
    apps instead of here.
    """
    @property
    def redis_server(self):
        from app import app
        return app.kvs

    @property
    def app_config(self):
        from app import app
        return app.config

    def authorize_request(self):

        sec_tokens = getattr(
            self, '{}_security_tokens'.format(request.method).lower())

        assert_user_has_any_permission(sec_tokens,
                                       redis=self.redis_server,
                                       app_conf=self.app_config,
                                       token_prefix=TOKEN_PREFIX,
                                       req=request)


class ListApiResource(DbSetApiMixin, ScoopAuthMixin, Resource):
    """
    Controller base class that provides a "GET" method, which returns a list
    of objects from the database.
    """
    list_request_parser = None

    serialized_list_name = 'objects'

    default_ordering = []
    default_filters = []

    get_security_tokens = []

    def _get_filters(self):
        """
        Using list_request_parser, returns a set of SqlAlchemyBinaryExpression
        objects, that are suitable for passing to a BaseQuery's filter()
        method.  Any BinaryExpressions that are defined in default_filters
        will be appended to the returned list, if there is not already filter
        provided for that argument.

        :return:
        """
        parser = get_or_create_instance(self.list_request_parser)

        filter_exps = parser.parse_args(req=request).get('filters')

        # fetch any default filters that weren't specifically overridden in
        # the request -- PS, I quite deeply HATE this idea of 'default filters'
        # and think we should strongly encourage the front end to EXPLICITLY
        # request what data they need.
        def_filters = [defexp for defexp in self.default_filters
                       if defexp.left.name
                       not in [reqexp.left.name for reqexp in filter_exps]]

        filter_exps.extend(def_filters)

        return filter_exps

    def _get_ordering(self):
        # if we're sorting by any fields.
        # we can apply the sort against multiple columns
        # we support ascending/descending sorts
        ordering_parser = specialized.SqlAlchemyOrderingParser()

        ordering_options = ordering_parser.parse_args(req=request)

        result = ordering_options.get('order')

        return result or self.default_ordering

    def _get_pagination(self):
        # setup our query offset + limit.
        # used for pagination
        pagination_parser = specialized.PaginationParser()
        pagination_options = pagination_parser.parse_args(req=request)
        return pagination_options['limit'], pagination_options['offset']

    def _get_list_serializer(self):

        serializer = serializers.PaginatedSerializer(self._get_serializer(),
                                                     self.serialized_list_name)
        return serializer

    def _get_list_viewmodel(self, limit, offset):
        return viewmodels.ListViewmodel(
            self.query_set,
            element_viewmodel=self._get_viewmodel,
            limit=limit,
            offset=offset,
            ordering=self._get_ordering(),
            filtering=self._get_filters())

    def get(self):
        """
        Returns a paginated list of object, wrapped inside of a ListViewModel.

        Allowed query argumens:
        * fields={csv list of field names}

        :return: A python list of Banners.
        :rtype: :py:class:`app.banners.models.Banner`
        :raises: :py:class:`werkzeug.exceptions.BadRequest`
        """
        self.authorize_request()

        view_model = self._get_list_viewmodel(*self._get_pagination())

        response = jsonify(marshal(view_model, self._get_list_serializer()))

        weak_etag = self._generate_weak_etag(view_model)
        response.set_etag(weak_etag, weak=True)

        return response.make_conditional(request)

    def _generate_weak_etag(self, list_viewmodel):
        if list_viewmodel.results:
            if hasattr(list_viewmodel.results[0], 'modified'):
                weak_etag = "".join(
                    [e.modified.isoformat() for e in list_viewmodel.results])
            else:
                weak_etag = "".join(str(e.id) for e in list_viewmodel.results)
        else:
            weak_etag = ""
        return md5(weak_etag).hexdigest()


class CreateApiResource(DbSetApiMixin, ScoopAuthMixin, Resource):
    """
    Controller base class that provides handles a "POST" method,
    to create a new object in the database.
    """
    create_request_parser = None

    on_create_skip_deserialization = []

    post_security_tokens = []

    def _get_create_parameters(self):

        if isinstance(self.create_request_parser, type):
            parser = self.create_request_parser()
        else:
            parser = self.create_request_parser

        return parser.parse_args(req=request)

    def _before_insert(self, model, req_data):
        """
        If you need any special functionality handled before your model
        is inserted into the database, override this method in your controller.

        :param class model: Model instance that will be saved in the database.
        """
        pass

    def _after_insert(self, model, req_data):
        pass

    def post(self):
        """
        Creates a new Banner in the database with the data provided
        in the request global variable.

        :return: A tuple containing the newly-created banner instance
            and int for HTTP status (201).
        :rtype: :py:class:`app.banners.models.Banner` and int
        :raises: :py:class:`werkzeug.exceptions.BadRequest`
        """
        self.authorize_request()

        req_data = self._get_create_parameters()

        model_type = self.query_set._primary_entity.type

        model = model_type(**{k: req_data[k] for k in req_data
                              if k not in self.on_create_skip_deserialization})

        self._before_insert(model, req_data)

        self.query_set.session.add(model)
        self.query_set.session.commit()

        self._after_insert(model, req_data)

        model.id

        return (marshal(self._get_viewmodel(model), self._get_serializer()),
                CREATED)


class ListCreateApiResource(CreateApiResource, ListApiResource):
    """
    A standard list endpoint that also provides a POST endpoint for creating
    new records.
    """
    # we have to explicitally define this because flask-restful's resolution
    # of methods in base classes is broken.
    methods = ('get', 'post', )


class ReadDetailApiResource(DbSetApiMixin, ScoopAuthMixin, Resource):

    get_security_tokens = []

    def get(self, db_id):
        """
        Retrieves a single object from the database, based on it's id attribute.

        :param `int` db_id: Primary key of the object to retrieve.
        :return: A dictionary representation of the object requested.
        :rtype: dict
        :raises: :py:class:`werkzeug.exceptions.NotFound`
        :raises: :py:class:`flask_restful.fields.MarshallingException`
        """
        self.authorize_request()

        model = self.query_set.get_or_404(db_id)

        return marshal(self._get_viewmodel(model),
                               self._get_serializer())


class UpdateApiResource(DbSetApiMixin, ScoopAuthMixin, Resource):

    put_security_tokens = []

    update_request_parser = None

    on_update_skip_deserialization = []

    def put(self, db_id):
        """
        Updates a single object in the database with the data provided in
        the request.  Attributes not present in the request json will be
        ignored (unless they are explicitally required by the REQUEST_PARSER.

        :param int db_id: Primary key of the object to update.
        :return: A dictionary representation of the object after the update.
        :rtype: dict
        :raises: :py:class:`werkzeug.exceptions.BadRequest`
        :raises: :py:class:`werkzeug.exceptions.NotFound`
        :raises: :py:class:`flask_restful.fields.MarshallingException`
        """
        self.authorize_request()

        model = self.query_set.get_or_404(db_id)

        parser = get_or_create_instance(self.update_request_parser)

        args = parser.parse_args(req=request)

        for attr_name, new_value in args.items():
            if attr_name in self.on_update_skip_deserialization:
                continue
            setattr(model, attr_name, new_value)

        self._before_update(model, args)

        self.query_set.session.commit()

        model.id

        return marshal(self._get_viewmodel(model),
                       self._get_serializer())

    def _before_update(self, model, req_args):
        pass


class SoftDeleteApiResource(DbSetApiMixin, ScoopAuthMixin, Resource):

    delete_security_tokens = []

    def delete(self, db_id):
        """
        Performs a 'soft delete' of an object, by setting it's "is_active"
        attribute to "False" and updating the database.

        :param int db_id:
        :return: A tuple, first element None, second element set to the response
            code for this method (always 204).
        :rtype: tuple(None, int)
        :raises: :py:class:`werkzeug.exceptions.NotFound`
        :raises: :py:class:`flask_restful.fields.MarshallingException`
        """
        self.authorize_request()

        model = self.query_set.get_or_404(db_id)
        model.is_active = False

        self.query_set.session.commit()

        return None, NO_CONTENT


class DetailApiResource(ReadDetailApiResource,
                        UpdateApiResource,
                        SoftDeleteApiResource):
    """
    Common base class for API endpoints that fetch, update, and soft-delete
    records from our database.
    """
    methods = ('get', 'put', 'delete', )
