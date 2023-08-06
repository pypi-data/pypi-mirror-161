# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class FingerprintBrowser(pydantic.BaseModel):
    name: str = pydantic.Field(..., alias='browserName')
    device: str
    user_agent: str = pydantic.Field(..., alias="userAgent")

    class Config:
        allow_population_by_field_name: bool = True
