# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import functools
import logging
from typing import Any
from typing import Callable
from typing import Generator

import cryptography.exceptions
import fastapi
import pydantic
from cbra.conf import settings
from ckms.jose import PayloadCodec
from unimatrix.exceptions import CanonicalException

from cbra.ext import ioc
from cbra.params import ServerCodec
from cbra.params import CurrentServer
from cbra.session import BaseSession
from cbra.session.const import SESSION_COOKIE_NAME
from cbra.session.const import SESSION_ENCRYPTION_KEYS
from ckms.jose import PayloadCodec

from libwebid.types import SessionClaims


class CookieIdentifiedDistributedSession(BaseSession):
    __module__: str = 'libwebid.lib'
    audience: set[str] = settings.SESSION_COOKIE_AUDIENCE
    codec: PayloadCodec
    dirty: set[str]
    domain: str = settings.SESSION_COOKIE_DOMAIN
    encrypted_cookie: str
    issuer: str
    logger: logging.Logger = logging.getLogger('uvicorn')
    model: type[SessionClaims] = SessionClaims
    token_type: str = "jwt+session"
    readonly: bool = False
    request: fastapi.Request
    samesite: str = 'strict'
    sessions: Any
    session_id: int | None

    @staticmethod
    def require_deserialized(
        func: Callable[..., Any]
    ) -> Callable[..., Any]:
        @functools.wraps(func)
        def f(self: Any, *args: Any, **kwargs: Any) -> Any:
            if self.claims == self.awaiting:
                raise RuntimeError("Session is not loaded.")
            return func(self, *args, **kwargs)

        return f

    def __init__(
        self,
        request: fastapi.Request,
        codec: PayloadCodec = ServerCodec,
        issuer: str = CurrentServer,
        sessions: Any = ioc.instance('SessionRepository'),
        encrypted_cookie: str = fastapi.Cookie(
            default=None,
            alias=SESSION_COOKIE_NAME,
            title="Session",
            description=(
                "Identifies the current session associated to the user agent."
            )
        )
    ):
        self.claims = self.awaiting
        self.codec = codec
        self.dirty = set()
        self.encrypted_cookie = encrypted_cookie
        self.issuer = issuer
        self.request = request
        self.sessions = sessions
        self.session_id = None
        if request is not None:
            request.scope['session'] = self

    @require_deserialized
    def get(self, key: str) -> Any:
        assert isinstance(self.claims, dict), type(self.claims) # nosec
        return self.claims.get(key) # type: ignore

    @require_deserialized
    def set(self, key: str, value: Any) -> None:
        self.dirty.add(key)
        self.claims[key] = value # type: ignore

    async def add_to_response(self, response: fastapi.Response) -> None:
        if self.claims == self.awaiting:
            # The session was not used at all.
            return
        if self.readonly or (not self.dirty and not self.created):
            return
        if self.claims and self.dirty:
            await self.sessions.persist(self.model.parse_obj(self.claims))

    async def _deserialize(self) -> None:
        now = int(datetime.datetime.utcnow().timestamp())
        if self.encrypted_cookie is None:
            self.created = True
            self.claims = {'iat': now}
        elif self.claims == self.awaiting:
            assert self.encrypted_cookie is not None
            try:
                _, claims = await self.codec.jwt(
                    token=str.encode(self.encrypted_cookie, 'ascii'),
                    accept="jwt+session"
                )
                claims.verify(audience=self.audience or {self.issuer})
                self.session_id = int(claims.extra.get('id') or 0)
                self.claims = dict(await self.sessions.get(self.session_id))
            except (CanonicalException, cryptography.exceptions.InvalidTag) as exception:
                # The session was tampered with or we rotated the session key.
                self.logger.critical(
                    "Caught %s while decoding session cookie. "
                    "Session was probably tampered with.",
                    type(exception).__name__
                )
                self.created = True
                self.claims = {'iat': now}
            except Exception as exception:
                self.logger.exception("Caught fatal %s", type(exception).__name__)
                self.created = True
                self.claims = {'iat': now}

    def __await__(self) -> Generator[pydantic.BaseModel, None, None]:
        return self._deserialize().__await__()