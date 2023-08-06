# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from cbra.types import Request
from cbra.types import IParser
from ..exceptions import ParseError


class JWTParser(IParser):
    """Parses the JSON Web Encryption (JWE) or JSON Web Signature (JWS)
    from the request body and decodes the payload as a JSON Web
    Token (JWT).
    """
    media_type: str = "application/jwt"
    token_types: set[str] = {"jwt"}

    async def parse(
        self,
        request: Request,
        media_type: str | None = None,
        parser_context: dict[str, Any] | None = None
    ) -> Any:
        """Parse the request body to a JSON Web Signature (JWS) and
        return the payload as a :class:`~ckms.types.JSONWebToken`
        instance. The signature of the JWS and the claims of the JWT
        are not verified and validated.
        
        If the request body is JSON Web Encryption (JWE), the :meth:`parse()`
        method uses the :attr:`~cbra.Application.keychain` to decrypt the
        payload.

        A :exc:`~cbra.exceptions.ParseError` is raised if the JOSE object in
        the request body is malformed, is not a JWS or if the payload of the
        JWS is not a JWT.

        The following failure status may be produced by :meth:`parse()`:

        - `MALFORMED_BODY` - The request body could not be decrypted,
          or the decrypted object could not be parsed as a JWS/JWT.
        - `INVALID_TOKEN_TYPE` - The request body was succesfully decrypted
          and the JOSE header could be interpreted, but its ``typ`` claim
          specified a value that is not accepted by the parser.
        """
        try:
            jws = await request.codec.jws(await request.body())
        except Exception:
            raise ParseError(
                code="MALFORMED_BODY",
                message=(
                    "The request body could not be parsed as a JSON "
                    "Web Signature (JWS)."
                )
            )
        if not jws.is_jwt(self.token_types):
            raise ParseError(
                code="INVALID_TOKEN_TYPE",
                message=(
                    "The payload of the JSON Web Signature (JWS) is not a JSON "
                    "Web Token (JWT) or the JOSE header declared a 'typ' claim "
                    "that is not accepted by the server."
                )
            )
        return jws