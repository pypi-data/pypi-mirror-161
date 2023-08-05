from ckms.core import Keychain

import cbra
from cbra.ext.jwks import JWKSEndpoint


__all__ = ['get_asgi_application']


def get_asgi_application() -> cbra.Application:
    keychain = Keychain()
    keychain.configure({ # type: ignore
        'sig': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RS256',
            'key': {'length': 2048},
            'tags': ['server'],
        },
        'enc': {
            'provider': 'local',
            'kty': 'RSA',
            'algorithm': 'RSA-OAEP-256',
            'key': {'length': 2048},
            'tags': ['server'],
        }
    })
    app = cbra.Application(
        keychain=keychain
    )
    app.add(JWKSEndpoint)
    return app


app = get_asgi_application()
if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)
