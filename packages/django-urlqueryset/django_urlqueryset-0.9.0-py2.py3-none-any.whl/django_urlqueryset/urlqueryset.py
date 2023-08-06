import json
import logging
from datetime import datetime

import requests
from django.conf import settings
from django.core import serializers
from django.db import models
from django.db.models.query import ModelIterable, QuerySet
from django.db.models.sql import Query
from django.db.models.sql.where import WhereNode
from requests import HTTPError
from rest_framework.exceptions import ValidationError
from urllib.parse import urlencode
from django.core.serializers import base

from django_urlqueryset.utils import get_default_params

logger = logging.getLogger(__name__)


class UrlModelIterable(ModelIterable):
    def __iter__(self):
        return self.queryset.deserialize(self.queryset._result_cache)


class UrlQuery:
    def __init__(self, model, where=WhereNode, alias_cols=True, **kwargs):
        self.model = model
        self.filters = {}
        self.high_mark = None
        self.low_mark = 0
        self.nothing = False


        self.alias_refcount = {}
        # alias_map is the most important data structure regarding joins.
        # It's used for recording which joins exist in the query and what
        # types they are. The key is the alias of the joined table (possibly
        # the table name) and the value is a Join-like object (see
        # sql.datastructures.Join for more information).
        self.alias_map = {}
        # Whether to provide alias to columns during reference resolving.
        self.alias_cols = alias_cols
        # Sometimes the query contains references to aliases in outer queries (as
        # a result of split_exclude). Correct alias quoting needs to know these
        # aliases too.
        # Map external tables to whether they are aliased.
        self.external_aliases = {}
        self.table_map = {}  # Maps table names to list of aliases.
        self.default_cols = True
        self.default_ordering = True
        self.standard_ordering = True
        self.used_aliases = set()
        self.filter_is_sticky = False
        self.subquery = False
        # SQL-related attributes
        # Select and related select clauses are expressions to use in the
        # SELECT clause of the query.
        # The select is used for cases where we want to set up the select
        # clause to contain other than default fields (values(), subqueries...)
        # Note that annotations go to annotations dictionary.
        self.select = ()
        self.where = where()
        self.where_class = where
        # The group_by attribute can have one of the following forms:
        #  - None: no group by at all in the query
        #  - A tuple of expressions: group by (at least) those expressions.
        #    String refs are also allowed for now.
        #  - True: group by all select fields of the model
        # See compiler.get_group_by() for details.
        self.group_by = None
        self.order_by = ()
        self.distinct = False
        self.distinct_fields = ()
        self.select_for_update = False
        self.select_for_update_nowait = False
        self.select_for_update_skip_locked = False
        self.select_for_update_of = ()
        self.select_for_no_key_update = False
        self.select_related = False
        # Arbitrary limit for select_related to prevents infinite recursion.
        self.max_depth = 5
        # Holds the selects defined by a call to values() or values_list()
        # excluding annotation_select and extra_select.
        self.values_select = ()
        # SQL annotation-related attributes
        self.annotations = {}  # Maps alias -> Annotation Expression
        self.annotation_select_mask = None
        self._annotation_select_cache = None
        # Set combination attributes
        self.combinator = None
        self.combinator_all = False
        self.combined_queries = ()
        # These are for extensions. The contents are more or less appended
        # verbatim to the appropriate clause.
        self.extra = {}  # Maps col_alias -> (col_sql, params).
        self.extra_select_mask = None
        self._extra_select_cache = None
        self.extra_tables = ()
        self.extra_order_by = ()
        # A tuple that is a set of model field names and either True, if these
        # are the fields to defer, or False if these are the only fields to
        # load.
        self.deferred_loading = (frozenset(), True)
        self._filtered_relations = {}
        self.explain_query = False
        self.explain_format = None
        self.explain_options = {}

    @property
    def is_sliced(self):
        return self.low_mark != 0 or self.high_mark is not None

    def get_meta(self):
        return self.model._meta

    def set_limits(self, low=None, high=None):
        if high is not None:
            if self.high_mark is not None:
                self.high_mark = min(self.high_mark, self.low_mark + high)
            else:
                self.high_mark = self.low_mark + high
        if low is not None:
            if self.high_mark is not None:
                self.low_mark = min(self.high_mark, self.low_mark + low)
            else:
                self.low_mark = self.low_mark + low

        if self.low_mark == self.high_mark:
            self.set_empty()

    def set_empty(self):
        self.nothing = True

    def clear_ordering(self, force_empty):
        self.order_by = ()

    def add_ordering(self, *ordering):
        if ordering:
            self.order_by += ordering

    def clone(self):
        new = self.__class__(self.model)
        new.filters = self.filters.copy()
        new.high_mark = self.high_mark
        new.low_mark = self.low_mark
        new.nothing = self.nothing
        new.order_by = self.order_by
        return new

    def can_filter(self):
        return True

    def chain(self):
        return self.clone()

    def add_q(self, q_object):
        self.filters.update(dict(q_object.children))

    def _execute(self, request_params, user=None, method='get', **kwargs):
        filters = self.filters
        if self.high_mark is None:
            self.high_mark = settings.URLQS_HIGH_MARK
        query_params = {
            'offset': self.low_mark,
            'limit': self.high_mark - self.low_mark
        }
        if self.order_by:
            query_params['ordering'] = ','.join(self.order_by)
        elif self.get_meta().ordering:
            query_params['ordering'] = ','.join(self.get_meta().ordering)
        if 'search' in filters:
            query_params['search'] = filters['search']
            filters.pop('search')

        _request_params = get_default_params(user)
        _request_params.update(request_params.copy())
        _request_params.update(kwargs)
        # fetch_method is used to change the method of list action of a model
        fetch_method = _request_params.pop('fetch_method')
        url = _request_params.pop('url').replace('{{model._meta.model_name}}', self.model._meta.model_name)
        url = f"{url}?{urlencode(query_params, safe=',')}"
        for key, value in filters.items():
            if key.endswith('__in') and isinstance(value, (list, tuple)):
                filters[key] = ",".join(str(i) for i in value)
            if isinstance(value, datetime):
                filters[key] = value.strftime('%Y-%m-%d %H:%M')
        if filters and fetch_method == 'post' and method == 'get':
            method = fetch_method
            _request_params['json'] = filters
        elif filters:
            url = f"{url}&{urlencode(filters, safe=',')}"
        response = getattr(requests, method)(url=url, **_request_params)
        response.raise_for_status()
        return response.json() if response.headers.get('Content-Type') == 'application/json' else response


class UrlQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        self.request_params = kwargs.pop('request_params', {})
        super().__init__(*args, **kwargs)
        if isinstance(self.query, Query):
            self.query = UrlQuery(self.model)
        self._iterable_class = UrlModelIterable
        self._count = None
        self._result_cache = None
        self.logged_user = None

    def count_with_result(self):
        """
        This is the equivalent of list(queryset) + queryset.count() in one operation(http call)
        :return:
        """
        self._fetch_all()
        return self._count, self._result_cache

    def _clone(self):
        c = super()._clone()
        c.request_params = self.request_params
        c.logged_user = self.logged_user
        return c

    def as_manager(cls, **request_params):
        from django.db.models.manager import Manager

        class _Manager(Manager.from_queryset(cls)):
            def get_queryset(self):
                queryset = super().get_queryset()
                queryset.request_params = self.request_params
                return queryset
        manager = _Manager()
        manager._built_with_as_manager = True
        manager.request_params = request_params
        return manager
    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)

    def count(self):
        if self._count is None:
            qs = self._chain()
            qs.query.set_limits(0, 1)
            return qs.query._execute(self.request_params)[settings.URLQS_COUNT]
        return self._count

    def _fetch_all(self):
        if self._count is None:
            response = self.query._execute(self.request_params, user=self.logged_user)
            self._result_cache = list(self.deserialize(response[settings.URLQS_RESULTS]))
            self._count = response[settings.URLQS_COUNT]

    def create(self, **kwargs):
        if self.request_params.get('fetch_method') == 'post':
            raise ValidationError({'remote_api_error': 'Create not available'})
        try:
            response = self.query._execute(self.request_params, user=self.logged_user, method='post', json=kwargs)
            return list(self.deserialize([response]))[0]
        except HTTPError as e:
            raise ValidationError({'remote_api_error': e.response.json()})

    def delete(self, **kwargs):
        try:
            response = self.query._execute(self.request_params, user=self.logged_user, method='delete', json=kwargs)
            return response
        except HTTPError as e:
            raise ValidationError({'remote_api_error': e.response.json()})

    def update(self, **kwargs):
        return self._chain().query._execute(self.request_params, user=self.logged_user, method='patch', json=kwargs)

    def deserialize(self, json_data=()):
        Model = self.model
        field_names = {f.name for f in Model._meta.get_fields()}  # Model: <list of field_names>
        related_fields = {}
        for field in Model._meta.fields:
            if field.related_model:
                related_fields[field.name] = {'manager': field.related_model.objects, 'pks': []}

        for obj_data in json_data:
            for field_name, value in related_fields.items():
                if field_name in obj_data and obj_data[field_name]:
                    related_fields[field_name]['pks'].append(obj_data[field_name])

        for rel_field, data in related_fields.items():
            if data['pks']:
                data['objs'] = {obj.pk: obj for obj in data['manager'].filter(pk__in=data['pks'])}

        for d in json_data:
            # Look up the model and starting build a dict of data for it.
            data = {}

            # Handle each field
            for (field_name, field_value) in d.items():
                if field_name not in field_names:
                    # skip fields no longer on model
                    continue
                field = Model._meta.get_field(field_name)

                # Handle M2M relations and FK fields
                if field_value and field.remote_field and isinstance(field.remote_field, (models.ManyToManyRel, models.ManyToOneRel)):
                    data[field_name] = related_fields[field_name]['objs'][field_value]
                # Handle all other fields
                else:
                    data[field.name] = field.to_python(field_value)

            yield Model(**data)

    def set_logged_user(self, user):
        clone = self._chain()
        clone.logged_user = user
        return clone

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        # if self._result_cache is not None:
        #     return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._chain()
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            qs.query.set_limits(start, stop)
            return list(qs)[::k.step] if k.step else qs

        qs = self._chain()
        qs.query.set_limits(k, k + 1)
        qs._fetch_all()
        return qs._result_cache[0]


