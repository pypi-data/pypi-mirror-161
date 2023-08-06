# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from ckms.core import models


class JSONWebSignature(pydantic.BaseModel):
    payload: str = pydantic.Field(
        ...,
        title="Payload",
        description=(
            "The URL-safe, Base64-encoded `payload` member contains the "
            "UTF-8 JSON-serialized JSON Web Key Set (JWKS) holding the "
            "keys that may be used to encrypt HTTP requests to this "
            "server."
        )
    )

    signatures: list[models.Signature] = pydantic.Field(
        ...,
        title="Signatures",
        description=(
            "An array of `Signature` objects. Compliant implementations **must** "
            "verify each item in the `signatures` array."
        )
    )