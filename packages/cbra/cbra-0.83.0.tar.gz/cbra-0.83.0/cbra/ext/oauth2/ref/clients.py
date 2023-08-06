# pylint: skip-file
from cbra.ext.oauth2 import ClientConfig
from cbra.ext.oauth2.types import GrantType


jwt: ClientConfig = ClientConfig(
    client_id='jwt',
    grant_types_supported=[
        GrantType.jwt_bearer.value
    ]
)