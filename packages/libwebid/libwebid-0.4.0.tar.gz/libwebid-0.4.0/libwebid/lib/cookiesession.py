# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra import session
from cbra.conf import settings


CookieSession: type[session.CookieSession] = session.CookieSession.configure(
    audience=settings.SESSION_COOKIE_AUDIENCE,
    domain=settings.SESSION_COOKIE_DOMAIN,
    samesite='strict'
)