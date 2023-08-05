# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Any
from typing import Literal

import pydantic


class Event(pydantic.BaseModel):
    __module__: str = 'cbra.ext.picqer.models'
    idhook: int = pydantic.Field(
        default=...,
        title="Webhook ID",
        description=(
            "Identifies the webhook that sent the event."
        )
    )

    name: str = pydantic.Field(
        default=...,
        title="Name",
        description="Human-readable name of the webhook."
    )

    event: str

    event_triggered_at: datetime.datetime = pydantic.Field(
        default=...,
        title="Triggered at",
        description=(
            "The date/time at which the event was triggered."
        )
    )

    data: dict[str, Any] = pydantic.Field(
        default=...,
        title="Data",
        description=(
            "The object on which the event specified by the `event` "
            "attribute occurred."
        )
    )

    @classmethod
    def new(cls, *, name: str, event: str) -> type['Event']:
        """Create a new model for the given event `event`."""
        return type(name, (cls,), {
            'event': pydantic.Field(
                default=...,
                title="Event",
                description=f'Is always `{event}`.'
            ),
            'Config': type('Config', (cls.Config,), {
                'title': f'Picqer{name}'
            }),
            '__annotations__': {
                'event': Literal[event] # type: ignore
            }
        })