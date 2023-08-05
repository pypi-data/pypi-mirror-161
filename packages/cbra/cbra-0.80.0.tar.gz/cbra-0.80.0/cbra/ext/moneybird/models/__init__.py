# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeAlias

from .event import Event


__all__: list[str] = [
    'Event'
]

InvoicePaid: type[Event] = Event.new(
    name='InvoicePaid',
    event="sales_invoice_state_changed_to_paid"
)

InvoiceDefaulted: type[Event] = Event.new(
    name='InvoiceDefaulted',
    event="sales_invoice_state_changed_to_late"
)


EventType: TypeAlias = (
    InvoicePaid | InvoiceDefaulted
)