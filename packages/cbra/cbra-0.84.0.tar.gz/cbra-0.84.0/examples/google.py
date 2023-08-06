import cbra
from cbra import Application
from cbra.ext.google import AortaEndpoint
from cbra.ext.google import CloudSchedulerEndpoint
from cbra.ext.google import EventarcEndpoint
from cbra.ext.google import GoogleEndpoint
from cbra.ext.google.models import MessagePublished


class EventarcMessageReceiver(EventarcEndpoint):
    pass


class ExportDailyStockList(CloudSchedulerEndpoint):
    summary: str = "Trigger stocklist export"
    response_description: str = "The stocklist is queued for export."

    async def handle(self):
        pass


class ExampleGoogleEndpoint(GoogleEndpoint):
    method: str = 'POST'

    async def handle(self):
        return {"email": self.principal.email if self.principal else "none"}


def get_asgi_application():
    app = Application()
    app.add(ExampleGoogleEndpoint, base_path='/')
    app.add(ExportDailyStockList, base_path='/export')
    app.add(AortaEndpoint, base_path='/aorta')
    app.add(EventarcMessageReceiver, base_path='/eventarc')
    return app


app = get_asgi_application()


@app.get('/foo')
def test(body: MessagePublished):
    pass


if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)
