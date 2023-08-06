# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .isessionclaims import ISessionClaims


class SessionClaims(pydantic.BaseModel, ISessionClaims):
    id: int | None = None
    auth_time: int | None = None
    mfa: int | None = None
    sub: int | None = None

    #: Metadata on the creation of the session. Should not be modified.
    request_id: str
    visitor_id: str