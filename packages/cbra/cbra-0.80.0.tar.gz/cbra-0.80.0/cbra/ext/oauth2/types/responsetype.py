"""Declares :class:`ResponseType`."""
import enum


class ResponseType(str, enum.Enum):
    __module__: str = 'cbra.ext.oauth2.types'
    code = "code"
    code_id_token = "code id_token"
    code_id_token_token = "code id_token token"
    code_token = "code token"
    id_token = "id_token"
    id_token_token = "id_token token"
    none = "none"
    token = "token"