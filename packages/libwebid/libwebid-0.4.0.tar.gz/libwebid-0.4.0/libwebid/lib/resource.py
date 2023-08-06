# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import cbra.resource
import pydantic
from cbra.auth import NullPrincipal
from cbra.types import ICorsPolicy

from libwebid.types import ClientSession
from .cors import CORSPolicy
from .cookiesession import CookieSession


class Resource(cbra.resource.Resource):
    __abstract__: bool = True
    cors_policy: type[ICorsPolicy] = CORSPolicy
    principal: ClientSession | NullPrincipal = NullPrincipal # type: ignore
    session: CookieSession

    async def dispatch(self, *args: Any, **kwargs: Any) -> Any:
        # Load the session and get the subject. Perform this
        # action here because doing it in the Principal
        # leads to duplicate decryption of the session.
        await self.session
        try:
            self.principal = ClientSession.parse_obj(self.session.claims)
        except pydantic.ValidationError:
            self.principal = NullPrincipal()
        return await super().dispatch(*args, **kwargs)