# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import functools
from typing import Any
from typing import Callable

import ddd
from cbra.conf import settings
from cbra.ext import ioc
from pydantic import BaseModel
from google.cloud.datastore import Client
from google.cloud.datastore import Entity
from google.cloud.datastore import Key
from google.cloud.datastore import Query


class GoogleDatastoreRepository(ddd.Repository):
    __module__: str = 'login.infra.repo'
    client: Client
    kind: str
    project: str = settings.GOOGLE_DATASTORE_PROJECT
    id_attname: str = 'id'
    model: type[BaseModel]

    @staticmethod
    async def run_in_executor(
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    def __init__(
        self,
        client: Client = ioc.inject('DatastoreClient')
    ):
        super().__init__()
        self.client = client

    def entity_factory(self, id: int | None = None, key: Key | None = None) -> Entity:
        return Entity(key=key or self.storage_key(id=id))

    def restore(self, entity: Entity | None) -> Any:
        if entity is None:
            return None
        instance = self.model.parse_obj(entity)
        return instance

    def storage_key(self, id: int | None = None) -> Key:
        return (
            self.client.key(self.kind, id) # type: ignore
            if id is not None
            else self.client.key(self.kind) # type: ignore
        )

    async def delete(self, entity_id: int):
        assert entity_id is not None # nosec
        await self.run_in_executor(
            self.client.delete, # type: ignore
            self.storage_key(entity_id)
        )

    async def get_entity_by_id(self, entity_id: int) -> Entity | None:
        return await self.run_in_executor(
            functools.partial(
                self.client.get, # type: ignore
                key=self.client.key(self.kind, entity_id) # type: ignore
            )
        )

    async def one(self, query: Query):
        """Run a query that is expected to yield exactly one result."""
        result = None
        for entity in await self.run_in_executor(query.fetch): # type: ignore
            if result is not None: # multiple objects returned
                raise Exception("Multiple entities returned")
            result = entity
        if result is None:
            raise self.DoesNotExist
        return result

    async def put(self, entity: Entity) -> Entity:
        await self.run_in_executor(self.client.put, entity) # type: ignore
        assert entity.key.id is not None # type: ignore # nosec
        return entity

    def query(self, kind: str | None = None) -> Query:
        return self.client.query(kind=kind or self.kind) # type: ignore