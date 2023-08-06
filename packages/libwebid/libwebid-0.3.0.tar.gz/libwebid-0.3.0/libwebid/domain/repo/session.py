# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import ddd

from libwebid.types import ISessionClaims


class SessionRepository(ddd.Repository):
    __module__: str = 'libwebid.domain.repo'

    async def get(self, session_id: int | None) -> ISessionClaims:
        raise NotImplementedError

    async def get_by_request_id(self, request_id: str) -> ISessionClaims | None:
        raise NotImplementedError

    async def persist(self, obj: ISessionClaims) -> int: # type: ignore
        raise NotImplementedError