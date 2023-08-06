# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic


class Event(pydantic.BaseModel):
    __module__: str = 'cbra.ext.moneybird.models'

    administration_id: str = pydantic.Field(
        default=...,
        title="Administration ID",
        description=(
            "The Moneybird administration in which the event occurred."
        )
    )

    webhook_id: str = pydantic.Field(
        default=...,
        title="Webhook ID",
        description=(
            "Identifies the webhook that sent the message."
        )
    )

    webhook_token: str = pydantic.Field(
        default=...,
        title="Token",
        description=(
            "A pre-shared secret that is used to verify that the event "
            "was sent by Moneybird."
        )
    )

    state: str | None = pydantic.Field(
        default=None,
        title="State",
        description=(
            "Describes the current state of the object on which the "
            "event occurred."
        )
    )

    entity_id: str = pydantic.Field(
        default=...,
        title="Entity ID",
        description=(
            "An identifier of the entity on which the event "
            "occurred."
        )
    )

    entity_type: str = pydantic.Field(
        default=...,
        title="Entity type",
        description=(
            "The type of the entity where the event occurred."
        )
    )

    entity: dict[str, Any] = pydantic.Field(
        default=...,
        title="Entity",
        description=(
            "Contains the entity on which the event occurred. Determine it's "
            "type by inspecting the `entity_type` attribute."
        )
    )

    @classmethod
    def new(cls, *, name: str, event: str) -> type['Event']:
        """Create a new model for the given event `event`."""
        return type(name, (cls,), {
            'action': pydantic.Field(
                default=...,
                title="Action",
                description=f'Is always `{event}`.'
            ),
            'Config': type('Config', (cls.Config,), {
                'title': f'Moneybird{name}'
            }),
            '__annotations__': {
                'action': Literal[event] # type: ignore
            }
        })