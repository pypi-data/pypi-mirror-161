# pylint: skip-file
# type: ignore
import dataclasses
import datetime
import os
import typing

import ckms
import fastapi
import httpx
import pydantic

import cbra
from cbra.ext import oauth2
from cbra.ext.oauth2 import ref
from cbra.ext import jwks


@dataclasses.dataclass
class Subject(oauth2.types.ISubject):
    sub: str
    client_id: str


class ClientRepository(oauth2.types.IClientRepository):

    async def exists(self, client_id: str) -> bool:
        return True

    async def get(self, client_id: str) -> oauth2.ClientConfig:
        return oauth2.ClientConfig(
            client_id=client_id,
            default_redirect_url="https://localhost:8000",
            redirect_uris=["https://localhost:8000"],
            response_types={oauth2.types.ResponseType.code}
        )


class SubjectRepository(oauth2.types.ISubjectRepository):

    async def get(self, subject_id, client_id):
        return Subject(sub=subject_id, client_id=client_id)


class IdinName(pydantic.BaseModel):
    initials: str | None
    last_name: str | None
    last_name_prefix: str | None
    gender: str | None

    def get_name(self) -> str:
        return f'{self.initials} {self.get_family_name()}'

    def get_family_name(self) -> str:
        family_name = self.last_name
        if self.last_name_prefix is not None:
            family_name = f'{self.last_name_prefix} {family_name}'
        return typing.cast(str, family_name)

    def as_claims(self) -> dict[str, typing.Any]:
        claims = {
            'initials': self.initials,
            'name': self.get_name(),
            'family_name': self.get_family_name()
        }
        if self.gender in {'male', 'female'}:
            claims['gender'] = self.gender
        return claims


class IdinAge(pydantic.BaseModel):
    date_of_birth: datetime.date | None


class IdinTransaction(pydantic.BaseModel):
    transaction_id: str
    status: str
    issuer_id: str | None = None
    bin: str | None = None
    name: IdinName | None
    age: IdinAge | None

    def as_claims(self):
        return {
            **self.name.as_claims(),
            'birthdate': str(self.age.date_of_birth),
        }


class IdinProvider(oauth2.UpstreamProvider):
    name: str = 'idin'
    base_url: str = 'https://idin.cmtelecom.com/idin/v1.0'
    allowed_idin_issuers: set[str] = {"ASNBNL21", "BUNQNL2A"}

    async def create_redirect(
        self,
        request: fastapi.Request,
        dto: oauth2.types.AuthorizationRequest
    ) -> str:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            if request.query_params.get('idin_issuer')\
            not in self.allowed_idin_issuers:
                raise oauth2.exceptions.Error(
                    error="invalid_request",
                    error_description="The given iDIN issuer was not valid.",
                    redirect_uri=dto.redirect_uri,
                    mode="redirect"
                )
            response = await client.post( # type: ignore
                url='/transaction',
                json={
                    'merchant_token': os.environ['CM_IDIN_MERCHANT_TOKEN'],
                    'entrance_code': dto.request_id,
                    'identity': True,
                    'name': True,
                    'gender': True,
                    'address': False,
                    'date_of_birth': True,
                    'issuer_id': request.query_params['idin_issuer'],
                    'merchant_return_url': self.reverse(request),
                    'language': 'nl'
                }
            )
            response.raise_for_status()
            result = response.json()
        dto.extra['idin_merchant_reference'] = result['merchant_reference']
        return result['issuer_authentication_url']

    def get_authorization_request_id(
        self,
        request: fastapi.Request
    ) -> str:
            return request.query_params['ec']

    async def process_response(
        self,
        request: fastapi.Request,
        params: oauth2.types.AuthorizationRequest
    ) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post( # type: ignore
                url='/status',
                json={
                    'merchant_token': os.environ['CM_IDIN_MERCHANT_TOKEN'],
                    'merchant_reference': params.extra['idin_merchant_reference'],
                    'transaction_id': request.query_params['trxid'],
                }
            )
            result = IdinTransaction(**response.json())
            if result.status != 'success':
                raise oauth2.exceptions.Error(
                    error="consent_required",
                    error_description="The iDIN authentication failed.",
                    redirect_uri=params.redirect_uri,
                    mode='redirect'
                )
            print(result)


app = cbra.Application(keychain=ckms.Keychain())
app.add(
    ref.get_oauth2_server(
        grant_types={
            "authorization_code",
            "client_credentials",
            "urn:ietf:params:oauth:grant-type:jwt-bearer",
        },
        signing_key='sig'
    ),
    base_path='/oauth2'
)
app.keychain.register({
    'sig': {
        'provider': 'local',
        'path': 'pki/ed448.key',
        'tags': ['oauth2'],
        'use': 'sig'
    },
    'enc': {
        'provider': 'local',
        'path': 'pki/rsa-enc.key',
        'tags': ['oauth2'],
        'alg': "RSA-OAEP-256",
        'use': 'enc'
    },
})

if __name__ == '__main__':
    cbra.run('__main__:app', reload=True)
