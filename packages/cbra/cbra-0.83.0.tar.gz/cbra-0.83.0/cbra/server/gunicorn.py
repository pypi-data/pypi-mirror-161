"""Declares :class:`GunicornServer`."""
import multiprocessing
import typing

import fastapi
import gunicorn.app.base
from unimatrix.conf import settings


class GunicornServer(gunicorn.app.base.BaseApplication):

    @staticmethod
    def number_of_workers():
        return (multiprocessing.cpu_count() * 2) + 1

    def __init__(self,
        app: fastapi.FastAPI,
        options: typing.Optional[dict] = None
    ):
        self.application = app
        self.options = options or {}
        self.options.update({
            'workers': settings.WEB_CONCURRENCY\
                or (self.number_of_workers() if not settings.DEBUG else 1)
        })
        self.options.setdefault('timeout', settings.HTTP_WORKER_TIMEOUT)
        self.options.setdefault('worker_class', 'uvicorn.workers.UvicornWorker')
        if settings.DEPLOYMENT_ENV == 'local':
            self.configure_local()

        super().__init__()

    def configure_local(self) -> None:
        """Configures the server to run in a local development environment."""
        if settings.LOCALHOST_SSL_CRT and settings.LOCALHOST_SSL_KEY:
            self.options.update({
                'certfile': settings.LOCALHOST_SSL_CRT,
                'keyfile': settings.LOCALHOST_SSL_KEY
            })

    def load_config(self) -> None:
        """Constructs the configuration from the parameters provided to the
        constructor.
        """
        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> fastapi.FastAPI:
        """Return the ASGI application handling incoming requests."""
        return self.application

