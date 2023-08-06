from django.http import Http404

from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin as BaseCreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import UpdateModelMixin as BaseUpdateModelMixin
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_201_CREATED


class BaseValuesViewset(viewsets.GenericViewSet):
    """
    A viewset that uses a values call to get all model/queryset data in
    a single database query, rather than delegating serialization to a
    DRF ModelSerializer.
    """

    # A tuple of values to get from the queryset
    # values = None
    # A map of target_key, source_key where target_key is the final target_key that will be set
    # and source_key is the key on the object retrieved from the values call.
    # Alternatively, the source_key can be a callable that will be passed the object and return
    # the value for the target_key. This callable can also pop unwanted values from the obj
    # to remove unneeded keys from the object as a side effect.
    field_map = {}

    def __init__(self, *args, **kwargs):
        super(BaseValuesViewset, self).__init__(*args, **kwargs)
        if not hasattr(self, "values") or not isinstance(self.values, tuple):
            raise TypeError("values must be defined as a tuple")
        self._values = tuple(self.values)
        if not isinstance(self.field_map, dict):
            raise TypeError("field_map must be defined as a dict")
        self._field_map = self.field_map.copy()

    def generate_serializer(self):
        queryset = getattr(self, "queryset", None)
        if queryset is None:
            try:
                queryset = self.get_queryset()
            except Exception:
                pass
        model = getattr(queryset, "model", None)
        if model is None:
            return Serializer
        mapped_fields = {v: k for k, v in self.field_map.items() if isinstance(v, str)}
        fields = []
        extra_kwargs = {}
        for value in self.values:
            try:
                model._meta.get_field(value)
                if value in mapped_fields:
                    extra_kwargs[mapped_fields[value]] = {"source": value}
                    value = mapped_fields[value]
                fields.append(value)
            except Exception:
                pass

        meta = type(
            "Meta",
            (object,),
            {
                "fields": fields,
                "read_only_fields": fields,
                "model": model,
                "extra_kwargs": extra_kwargs,
            },
        )
        CustomSerializer = type(
            "{}Serializer".format(self.__class__.__name__),
            (ModelSerializer,),
            {"Meta": meta},
        )

        return CustomSerializer

    def get_serializer_class(self):
        if self.serializer_class is not None:
            return self.serializer_class
        # Hack to prevent the renderer logic from breaking completely.
        self.__class__.serializer_class = self.generate_serializer()
        return self.__class__.serializer_class

    def _get_lookup_filter(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if lookup_url_kwarg not in self.kwargs:
            raise AssertionError(
                "Expected view %s to be called with a URL keyword argument "
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                "attribute on the view correctly."
                % (self.__class__.__name__, lookup_url_kwarg)
            )

        return {self.lookup_field: self.kwargs[lookup_url_kwarg]}

    def annotate_queryset(self, queryset):
        return queryset

    def _map_fields(self, item):
        for key, value in self._field_map.items():
            if callable(value):
                item[key] = value(item)
            elif value in item:
                item[key] = item.pop(value)
            else:
                item[key] = value
        return item

    def consolidate(self, items, queryset):
        return items

    def serialize(self, queryset):
        queryset = self.annotate_queryset(queryset)
        values_queryset = queryset.values(*self._values)
        return self.consolidate(
            list(map(self._map_fields, values_queryset or [])), queryset
        )

    def serialize_object(self, **filter_kwargs):
        try:
            filter_kwargs = filter_kwargs or self._get_lookup_filter()
            queryset = self.get_queryset().filter(**filter_kwargs)
            return self.serialize(self.filter_queryset(queryset))[0]
        except (IndexError, ValueError, TypeError):
            raise Http404(
                "No %s matches the given query." % queryset.model._meta.object_name
            )


class ListModelMixin(object):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page_queryset = self.paginate_queryset(queryset)

        if page_queryset is not None:
            queryset = page_queryset

        if page_queryset is not None:
            return self.get_paginated_response(self.serialize(queryset))

        return Response(self.serialize(queryset))


class RetrieveModelMixin(object):
    def retrieve(self, request, *args, **kwargs):
        return Response(self.serialize_object())


class ReadOnlyValuesViewset(BaseValuesViewset, RetrieveModelMixin, ListModelMixin):
    pass


class CreateModelMixin(BaseCreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        return Response(self.serialize_object(pk=instance.pk), status=HTTP_201_CREATED)


class UpdateModelMixin(BaseUpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(self.serialize_object())


class ValuesViewset(
    ReadOnlyValuesViewset, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
):
    pass
