# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from libwebid import domain
from libwebid.lib.repo.googledatastore import GoogleDatastoreRepository
from libwebid.types import ISessionClaims
from libwebid.types import SessionClaims


class SessionRepository(domain.SessionRepository, GoogleDatastoreRepository):
    kind: str = 'Session'

    async def get(self, session_id: int | None) -> ISessionClaims:
        if session_id is None:
            return SessionClaims()
        return self.restore(await self.get_entity_by_id(session_id)) or SessionClaims()

    async def get_by_request_id(self, request_id: str) -> SessionClaims | None:
        query = self.query()
        query.add_filter('request_id', '=', request_id) # type: ignore
        try:
            return await self.one(query)
        except self.DoesNotExist:
            return None

    async def persist(self, obj: SessionClaims) -> int: # type: ignore
        entity = self.entity_factory(id=obj.id)
        entity.update(obj.dict()) # type: ignore
        await self.put(entity)
        obj.id = entity.key.id # type: ignore
        assert obj.id is not None # nosec
        return obj.id