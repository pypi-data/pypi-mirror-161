"""Declares :class:`EnvelopeMetadata`."""
import typing

import pydantic


class EnvelopeMetadata(pydantic.BaseModel):
    __module__: str = 'cbra.models'
    id: typing.Optional[typing.Union[int, str]] = pydantic.Field(
        default=None,
        title="Object identifier",
        description=(
            "Identifies the resource uniquely accross all resource versions. This "
            "property must not be set on `create` actions, unless otherwise specified."
        )
    )
    links: typing.Dict[str, str] = pydantic.Field(
        default={},
        title="Links",
        description=(
            "Additional links related to the resource. Read only."
        )
    )

    labels: dict[str, str] = pydantic.Field(
        default={},
        title="Labels",
        description=(
            "Map of string keys and values that can be used "
            "to organize and categorize (scope and select) objects."
        )
    )

    annotations: dict[str, typing.Any] = pydantic.Field(
        default={},
        title="Annotations",
        description=(
            "Annotations is an unstructured key value map stored "
            "with a resource that may be set by external tools to "
            "store and retrieve arbitrary metadata. Consult the "
            "documentation to determine if this resource supports "
            "annotations."
        )
    )