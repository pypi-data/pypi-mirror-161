# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.exceptions import CanonicalException


class SessionRequired(CanonicalException):
    """Raised when a session needs to be established prior to
    invoking an endpoint.
    """
    __module__: str = 'cbra.session'
    http_status_code: int = 401
    code: str = 'SESSION_REQUIRED'
    message: str = (
        "This endpoint requires the client to establish a session prior "
        "to invocation."
    )