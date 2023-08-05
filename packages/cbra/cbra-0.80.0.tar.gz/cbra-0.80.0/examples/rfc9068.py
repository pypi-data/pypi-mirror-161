"""Create a :rfc:`9068` access token for use with the examples."""
import asyncio
import datetime
import secrets

import ckms
import ckms.jose


async def create_access_token(
    issuer: str = "https://localhost:8000",
    audience: str = "https://localhost:8000",
    ttl: int = 600,
) -> str:
    keychain = ckms.Keychain()
    keychain.register({
        'sig' :{
            'provider': 'local',
            'path': 'pki/ed448.key',
            'use': 'sig'
        }
    })
    await keychain.setup()
    now = int(datetime.datetime.utcnow().timestamp())
    codec = ckms.jose.PayloadCodec(signer=keychain)
    jwt = ckms.jose.JSONWebToken(
        client_id="test",
        jti=secrets.token_hex(),
        iss=issuer,
        aud=audience,
        sub="bob@cbra.unimatrixapis.localhost",
        iat=now,
        exp=now+ttl,
        nbf=now - 10,
        scope="god"
    )
    meta = keychain.get_key_metadata('sig')
    jws = await codec.encode(jwt)\
        .sign(
            algorithm='EdDSA',
            using='sig',
            claims={'kid': meta.get_signing_kid()}
        )
    return bytes.decode(bytes(jws))


if __name__ == '__main__':
    result = asyncio.run(create_access_token())
    print(result)