"""Declares :class:`AuthorizationCode`."""


class AuthorizationCode:
    __module__: str = 'cbra.ext.oauth2.types'
    code: str
    request_id: str

    def __init__(self, request_id: str, code: str):
        self.request_id = request_id
        self.code = code