import asyncio
from cbra.ext.picqer import WebhookEndpoint


BASE_URL = "https://molano.picqer.com"
EMAIL = "sales@molano.nl"
API_KEY = "eJ8PQRiGdHyCygYcrhUVwDJNhz8PjXMqy9jF3Nwomj7xdHUr"
HOOKS = [
    {
        'name': "urn:webhook:picqer:products.stock_changed:uplink.molano.nl",
        'event': "products.stock_changed",
        'address': "https://uplink.molano.nl/log-request"
    },
    {
        'name': "urn:webhook:picqer:orders.completed:uplink.molano.nl",
        'event': "orders.completed",
        'address': "https://uplink.molano.nl/log-request"
    },
]


async def main():
    await WebhookEndpoint.create_webhooks(
        hooks=HOOKS,
        secret='foo',
        email=EMAIL,
        api_key=API_KEY,
        base_url=BASE_URL
    )


if __name__ == '__main__':
    asyncio.run(main())
