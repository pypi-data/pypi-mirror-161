import fastapi

import cbra
from cbra.session import CookieSession


app = cbra.Application(
    docs_url='/'
)
app.keychain.register({
    'session-signing-key': {
        'provider': "local",
        'kty': "OKP",
        'alg': "EdDSA",
        'crv': 'Ed448',
        'use': 'sig'
    },
    'session-encryption-key': {
        'provider': "local",
        'public_kid': 'session-encryption-key',
        'kty': "oct",
        'alg': "dir",
        'use': 'enc',
        'length': 32
    }
})


class SessionEndpoint(cbra.Endpoint):
    document: bool = True
    method: str = "GET"
    session: CookieSession

    async def handle(self):
        await self.session
        return self.session.claims


@app.post('/session')
async def set(
    response: fastapi.Response,
    session: CookieSession = fastapi.Depends(),
    key: str = fastapi.Query('foo'),
    value: str = fastapi.Query(...)
):
    await session.set(key, value)
    await session.add_to_response(response=response)


app.add(SessionEndpoint, base_path='/session')
if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)