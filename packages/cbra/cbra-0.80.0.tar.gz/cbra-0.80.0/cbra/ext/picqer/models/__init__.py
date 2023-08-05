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
    'Event',
    'EventType',
    'OrderCreated',
    'OrderAllocated',
    'OrderClosed',
    'OrderStatusChanged',
    'OrderCompleted',
    'ProductChanged',
    'ProductFreeStockChanged',
    'ProductAssembledStockChanged',
    'ProductStockChanged',
]

OrderCreated: type[Event] = Event.new(
    name='OrderCreated',
    event='orders.created'
)

OrderAllocated: type[Event] = Event.new(
    name='OrderAllocated',
    event='orders.allocated'
)

OrderClosed: type[Event] = Event.new(
    name='OrderClosed',
    event='orders.closed'
)

OrderStatusChanged: type[Event] = Event.new(
    name='OrderStatusChanged',
    event='orders.status_changed'
)

OrderCompleted: type[Event] = Event.new(
    name='OrderCompleted',
    event='orders.completed'
)

ProductChanged: type[Event] = Event.new(
    name='ProductChanged',
    event='products.changed'
)

ProductFreeStockChanged: type[Event] = Event.new(
    name='ProductFreeStockChanged',
    event='products.free_stock_changed'
)

ProductAssembledStockChanged: type[Event] = Event.new(
    name='ProductAssembledStockChanged',
    event='products.assembled_stock_changed'
)

ProductStockChanged: type[Event] = Event.new(
    name='ProductStockChanged',
    event='products.stock_changed'
)

EventType: TypeAlias = (
    OrderCreated | OrderAllocated | OrderClosed |
    OrderStatusChanged | OrderCompleted |
    ProductChanged | ProductFreeStockChanged |
    ProductAssembledStockChanged |
    ProductStockChanged
)