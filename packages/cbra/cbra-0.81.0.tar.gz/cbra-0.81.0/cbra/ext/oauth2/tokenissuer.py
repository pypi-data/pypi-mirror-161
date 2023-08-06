"""Declares :class:`TokenIssuer`."""
import functools
import inspect
import typing
from cbra.ext.oauth2.types.iclient import IClient

from ckms.jose import PayloadCodec
from ckms.types import JSONWebToken
from ckms.types import Malformed

from .exceptions import InvalidClient
from .exceptions import InvalidGrant
from .exceptions import InvalidScope
from .exceptions import ForbiddenScope
from .exceptions import AssertionReplayed
from .params import CurrentServerMetadata
from .params import LocalIssuer
from .params import ServerCodec
from .params import SubjectRepository
from .params import TransientStorage
from .types import AuthorizationCodeGrant
from .types import BaseGrant
from .types import ClientCredentialsGrant
from .types import GrantType
from .types import IStorage
from .types import ISubject
from .types import ISubjectRepository
from .types import ITokenIssuer
from .types import JWTBearerAssertionGrant
from .types import ServerMetadata
from .types import TokenResponse
from .utils import classproperty # type: ignore


class TokenIssuer(ITokenIssuer):
    """Issues a token for various grant types."""
    __module__: str = 'cbra.ext.oauth2'

    #: The transient storage used.
    storage: IStorage

    @classproperty
    def grant_types_supported(cls) -> typing.List[str]:
        return [
            GrantType.authorization_code.value,
            GrantType.client_credentials.value,
            GrantType.jwt_bearer.value
        ]

    def __init__(
        self,
        subjects: ISubjectRepository = SubjectRepository,
        codec: PayloadCodec = ServerCodec,
        metadata: ServerMetadata = CurrentServerMetadata,
        issuer: str = LocalIssuer,
        storage: IStorage = TransientStorage
    ):
        self.subjects = subjects
        self.codec = codec
        self.metadata = metadata
        self.issuer = issuer
        self.storage = storage

    def is_local_issued(self, claims: JSONWebToken) -> bool:
        """Return a boolean indicating if the claimset was issued
        by the local server.
        """
        return self.issuer == claims.iss

    @functools.singledispatchmethod
    async def grant(
        self,
        dto: BaseGrant
    ) -> TokenResponse:
        """Dispatches a request to the **Token Endpoint** to the
        appropriate handler for its ``grant_type``.
        """
        raise NotImplementedError(dto.grant_type)

    @grant.register
    async def grant_authorization_code(
        self,
        grant: AuthorizationCodeGrant
    ) -> TokenResponse:
        client = grant.get_client()
        _, request = await self.storage.get_code(grant.code)

        assert request.is_authenticated() # nosec
        subject = await request.get_subject(client.client_id, self.subjects)
        request.validate_grant(client, subject, grant)
        self.validate_grant(
            client=client,
            subject=subject,
            grant=grant
        )

        assert subject is not None # nosec
        return TokenResponse(
            access_token=await client.issue_token(
                codec=self.codec,
                algorithm='EdDSA',
                using='sig',
                issuer=self.issuer,
                audience=grant.get_audience(),
                subject=subject,
                ttl=self.default_ttl,
                scope=request.scope
            ),
            token_type="Bearer",
            expires_in=self.default_ttl,
            id_token=None,
            state=None,
            refresh_token=None
        )

    @grant.register
    async def grant_client_credentials(
        self,
        grant: ClientCredentialsGrant
    ) -> TokenResponse:
        # Client credentials grant is only available for confidential
        # clients.
        client = grant.get_client()
        if not client.is_confidential():
            raise InvalidClient(
                error="invalid_client",
                error_description=(
                    "The \"client_credentials\" grant is only available "
                    "for confidential clients."
                )
            )
        if grant.scope is not None and not client.allows_scope(grant.scope):
            raise ForbiddenScope

        # If the request does not include a "resource" parameter, the authorization
        # server MUST use a default resource indicator in the "aud" claim (RFC 9068,
        # Section 3).
        if not grant.resource:
            grant.resource.add(self.issuer) # type: ignore
        if len(grant.resource) > 1 and not client.can_issue_multiple():
            raise InvalidGrant(
                error_description=(
                    "The client refuses to issue access tokens for multiple "
                    "audiences."
                )
            )
        if not client.allows_audience(self.issuer, grant.resource):
            raise InvalidGrant(
                error_description=(
                    "The resource(s) specified in the request is not allowed "
                    "by the client."
                )
            )
        return TokenResponse(
            access_token=await client.issue_token(
                codec=self.codec,
                algorithm='EdDSA',
                using='sig',
                issuer=self.issuer,
                audience=grant.get_audience(),
                subject=client.as_subject(),
                ttl=self.default_ttl,
                scope=set(grant.scope or [])
            ),
            token_type="Bearer",
            expires_in=self.default_ttl,
            id_token=None,
            state=None,
            refresh_token=None
        )

    @grant.register
    async def grant_jwt_bearer(
        self,
        dto: JWTBearerAssertionGrant
    ) -> TokenResponse:
        client = dto.get_client()
        try:
            jws, claims = await self.codec.jwt(dto.assertion)
        except (Malformed, ValueError, TypeError):
            raise InvalidGrant(
                error_description=(
                    "The assertion is malformed and could not be interpreted "
                    "as a JSON Web Token (JWT)."
                )
            )
        claims.verify(
            audience={self.metadata.token_endpoint},
            max_age=self.max_assertion_age,
            required={'iss', 'aud', 'sub', 'iat', 'exp', 'nbf', 'jti'}
        )

        # Check if the assertion is not being replayed.
        if await self.storage.consume(claims):
            raise AssertionReplayed

        # There are two cases that need to be handled here, either the
        # claims are self-signed (a public key is preregistered for the
        # subject specified in the `sub` claim), or the claims were
        # signed by a trusted third-party.
        subject = await self.subjects.get(
            client_id=client.client_id,
            subject_id=typing.cast(typing.Union[int, str], claims.sub)
        )
        if dto.scope is not None and not client.allows_scope(dto.scope):
            raise ForbiddenScope
        if not subject.allows_scope(set(dto.scope or [])):
            raise InvalidScope

        # Lookup the JWKS of the issuer as indicated by the `iss` claim,
        # or use the keys pre-registered by the resource owner if the claims
        # are self-signed.
        selfsigned = claims.is_selfsigned()
        if not selfsigned and not self.is_local_issued(claims):
            # The assertion was issued and signed by a third-party.
            if not self.allow_jwks_lookups:
                raise InvalidGrant(
                    error_description=(
                        "The assertion was signed by a third-party, but it's "
                        "public keys are not known to the server and it does "
                        "not allow import using the JWKS URI."
                    )
                )
            if claims.iss not in self.trusted_issuers:
                raise InvalidGrant(
                    error_description=(
                        "The assertion was issued and signed by an issuer that is "
                        "not trusted by the server."
                    )
                )
            raise NotImplementedError
        elif not selfsigned:
            # The assertion was issued and signed by this server.
            raise InvalidGrant(
                error_description=(
                    "The assertion was issued and signed by an issuer that is "
                    "not trusted by the server."
                )
            )
        else:
            verifier = subject

        verified = verifier.verify(jws)
        if inspect.isawaitable(verified):
            verified = await verified
        if not verified:
            raise InvalidGrant(
                error_description=(
                    "The signature of the JWT assertion did not validate. Make "
                    "sure that the signing keys are pre-registered by the "
                    "resource owner."
                )
            )

        # If the request does not include a "resource" parameter, the authorization
        # server MUST use a default resource indicator in the "aud" claim (RFC 9068,
        # Section 3).
        if not dto.resource:
            dto.resource.add(self.issuer) # type: ignore
        if not client.allows_audience(self.issuer, set(dto.resource or [])):
            raise InvalidGrant(
                error_description=(
                    "Any or all of the audiences are not allowed by the client."
                )
            )

        token = await client.issue_token(
            codec=self.codec,
            algorithm='EdDSA',
            using='sig',
            issuer=self.issuer,
            audience=dto.get_audience(),
            subject=subject,
            ttl=self.default_ttl,
            scope=set(dto.scope or [])
        )
        return TokenResponse(
            access_token=token,
            token_type="Bearer",
            expires_in=self.default_ttl,
            id_token=None,
            state=None,
            refresh_token=None
        )

    def validate_grant(
        self,
        client: IClient,
        subject: ISubject | None,
        grant: BaseGrant
    ) -> None:
        """Validates the parameters provided by the grant and sets defaults."""
        # If the request does not include a "resource" parameter, the authorization
        # server MUST use a default resource indicator in the "aud" claim (RFC 9068,
        # Section 3).
        if not grant.resource:
            grant.resource.add(self.issuer) # type: ignore
        if not client.allows_audience(self.issuer, set(grant.resource or [])):
            raise InvalidGrant(
                error_description=(
                    "Any or all of the audiences are not allowed by the client."
                )
            )
        grant.validate_grant(client, subject)