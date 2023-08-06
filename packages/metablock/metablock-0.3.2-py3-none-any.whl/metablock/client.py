import logging
import os
import sys
from typing import Dict, Optional

from aiohttp import ClientSession

from .components import HttpComponent, MetablockResponseError
from .extensions import Extensions, Plugins
from .orgs import Orgs
from .spaces import Domains, Services, Space, Spaces
from .user import User

DEFAULT_USER_AGENT = f"Python/{'.'.join(map(str, sys.version_info[:2]))} metablock"

logger = logging.getLogger("metablock.client")


class Metablock(HttpComponent):
    """Metablock client"""

    url: str = os.environ.get("METABLOCK_URL", "https://api.metablock.io/v1")
    auth_key: str = os.getenv("METABLOCK_API_TOKEN", "")

    def __init__(
        self,
        url: str = None,
        auth_key: str = "",
        auth_key_name: str = "x-metablock-api-key",
        session: Optional[ClientSession] = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.url: str = url if url is not None else self.url
        self.auth_key: str = auth_key or self.auth_key
        self.auth_key_name = auth_key_name
        self.session: Optional[ClientSession] = session
        self.default_headers: Dict[str, str] = {
            "user-agent": user_agent,
            "accept": "application/json",
        }
        self.spaces: Spaces = Spaces(self)
        self.domains = Domains(self)
        self.orgs: Orgs = Orgs(self)
        self.services: Services = Services(self)
        self.plugins: Plugins = Plugins(self)
        self.extensions: Extensions = Extensions(self)

    def __repr__(self) -> str:
        return self.url

    __str__ = __repr__

    @property
    def cli(self):
        return self

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aenter__(self) -> object:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def spec(self):
        return await self.execute(f"{self.url}/spec")

    async def execute(
        self,
        url: str,
        method: str = "",
        headers: Optional[Dict[str, str]] = None,
        callback=None,
        wrap=None,
        timeout=None,
        **kw,
    ):
        if not self.session:
            self.session = ClientSession()
        method = method or "GET"
        headers_ = self.get_default_headers()
        headers_.update(headers or ())
        response = await self.session.request(method, url, headers=headers_, **kw)
        if callback:
            return await callback(response)
        if response.status == 204:
            return True
        if response.status >= 400:
            try:
                data = await response.json()
            except Exception:
                data = await response.text()
            raise MetablockResponseError(response, data)
        response.raise_for_status()
        data = await response.json()
        return wrap(data) if wrap else data

    async def get_user(self, callback=None) -> Dict:
        return await self.get(f"{self.url}/user", callback=callback, wrap=self._user)

    async def get_space(self, callback=None) -> Dict:
        return await self.get(f"{self.url}/space", callback=callback, wrap=self._space)

    async def update_user(self, callback=None, **data) -> Dict:
        return await self.patch(
            f"{self.url}/user", json=data, callback=callback, wrap=self._user
        )

    async def delete_user(self, callback=None) -> None:
        return await self.delete(f"{self.url}/user", callback=callback)

    def get_default_headers(self) -> Dict[str, str]:
        headers = self.default_headers.copy()
        if self.auth_key:
            headers[self.auth_key_name] = self.auth_key
        return headers

    def _user(self, data: Dict) -> User:
        return User(self, data)

    def _space(self, data: Dict) -> User:
        return Space(self.spaces, data)
