"""Declares :class:`ResourceMetaclass`."""
import typing
from cbra.resource.iresource import IResource

import inflect
from pydantic import dataclasses

from cbra.endpointmetaclass import EndpointMetaclass
from .basefiltermodel import BaseFilterModel
from .pathparameter import PathParameter


engine = inflect.engine()
VOWEL_CHARS = {'a', 'e', 'i', 'o', 'u'}


class ResourceMetaclass(EndpointMetaclass):

    @staticmethod
    def get_article(word: str):
        return 'a' if str.lower(word[0]) not in VOWEL_CHARS else 'an'

    def __new__(
        cls,
        name: str,
        bases: typing.Tuple[typing.Type[type], ...],
        namespace: typing.Dict[str, typing.Any]
    ):
        super_new = super().__new__
        if namespace.get('__abstract__', False):
            return super_new(cls, name, bases, namespace)

        # Collect the attributes from the bases.
        base_attrs: dict[str, typing.Any] = {}
        for b in reversed(bases):
            if not isinstance(b, ResourceMetaclass):
                continue
            base_attrs.update(b.__dict__) # type: ignore

        # Construct the resource name from the name attribute, parent name or
        # class name.
        resource_name = namespace.get('name')\
            or base_attrs.get('name')\
            or str.replace(name, 'Resource', '')

        namespace.setdefault('name', name)
        namespace.setdefault('name_article', base_attrs.get('name_article') or cls.get_article(resource_name))
        namespace.setdefault('pluralname', engine.plural(resource_name))
        if 'verbose_name' not in namespace:
            namespace['verbose_name'] = base_attrs.get('verbose_name') or str.title(namespace['name'])
        if 'verbose_name_plural' not in namespace:
            namespace['verbose_name_plural'] = engine.plural(str.title(namespace['verbose_name']))
        # If resource class is a subresource, then a parent member is
        # contained by the namespace.
        parent: ResourceMetaclass = namespace.get(
            'parent',
            base_attrs.get('parent')
        )

        # Construct the path parameters, including those defined by
        # the parent classes.
        if 'path_parameter' in namespace:
            path_parameter = namespace['path_parameter'] = PathParameter(
                name=namespace['path_parameter'],
                annotation=namespace.pop('path_parameter_class', None)
            )
        else:
            path_parameter = base_attrs.get('path_parameter')

        # Construct a pydantic model holding the query parameters.
        annotations = namespace.setdefault('__annotations__', {})
        #if 'query_parameters' in namespace and not namespace.get('query_model'):
        #    model_attrs: typing.Dict[typing.Any, typing.Any] = {}
        #    model_hints: typing.Dict[typing.Any, typing.Any] = {}
        #    for i, param in enumerate(namespace.pop('query_parameters', [])):
        #        if param.alias is None:
        #            raise ValueError(
        #                f"{name}.query_parameters[{i}] must set the "
        #                "'alias' parameter."
        #            )
        #        if QueryOptions.is_reserved_field(param.alias):
        #            raise ValueError(f"The name '{param.alias}' is reserved.")
        #        if not isinstance(param, fastapi.params.Query):
        #            raise NotImplementedError
        #        model_attrs[param.alias] = param
        #        model_hints[param.alias] = param.extra.pop('annotation', None) or str
        #    if model_attrs:
        #        annotations['query'] = namespace['query'] = dataclasses.dataclass(
        #            type(
        #                f'EndpointQuery',
        #                (BaseQueryModel,),
        #                {**model_attrs, '__annotations__': model_hints}
        #            )
        #        )

        attrs: dict[str, typing.Any] = {}
        for base in reversed(bases):
            attrs.update(base.__dict__) # type: ignore
        attrs.update(namespace)

        # Construct the filter model, which is used by the actions listed
        # by the filter_actions attribute.
        filter_name = str.replace(name, 'Resource', '')
        filter_model = type(f'{filter_name}FilterModel', (BaseFilterModel,), {})
        if attrs.get('searchable'):
            filter_params = namespace.pop('filter_defaults', [])
            for base in bases:
                if not hasattr(base, 'filter_defaults'):
                    continue
                filter_params.extend(base.filter_defaults) # type: ignore
            filter_attrs = {}
            for filter_param in filter_params:
                filter_param.add_to_namespace(filter_attrs)
            filter_model = type(f'{filter_name}FilterModel', (BaseFilterModel,), filter_attrs)
        annotations['query'] = namespace['query'] = dataclasses.dataclass(filter_model)

        # Create the new class with the updated namespace.
        new_class: type[IResource] = typing.cast(
            type[IResource],
            super_new(cls, name, bases, {
                **namespace,
            })
        )

        # The path parameter is required to determine the path for the
        # collection endpoints.
        if new_class.subresources and not new_class.path_parameter:
            raise ValueError(
                f"{name}.path_parameter can not be None because "
                f"{name}.subresources is a non-empty list."
            )

        # Set the parent attribute on the subresources. This is used to
        # determine the path parameters.
        for i, child in enumerate(new_class.subresources):
            new_class.subresources[i] = typing.cast(
                type[IResource],
                child.new(parent=new_class)
            )

        return new_class