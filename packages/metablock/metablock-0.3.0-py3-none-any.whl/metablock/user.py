from typing import Dict, List

from .components import MetablockEntity, MetablockResponseError
from .orgs import Org, Orgs


class User(MetablockEntity):
    """Object representing a Metablock user"""

    @property
    def url(self) -> str:
        return f"{self.root.url}/user"

    async def orgs(self) -> List[Org]:
        """List user organizations"""
        orgs = Orgs(self.root)
        return await self.cli.get(
            f"{self.url}/orgs", wrap=lambda dl: [Org(orgs, d) for d in dl]
        )

    async def get_permissions(self, **kwargs) -> List[Dict]:
        """List user permissions"""
        return await self.cli.get(f"{self.url}/permissions", **kwargs)

    async def tokens(self) -> List[Dict]:
        return await self.cli.get(f"{self.url}/tokens")

    async def create_token(self) -> Dict:
        return await self.cli.post(f"{self.url}/tokens")

    async def delete_token(self, token_id: str) -> Dict:
        return await self.cli.delete(f"{self.url}/tokens/{token_id}")

    async def check_password(self, password: str) -> bool:
        try:
            return await self.root.post(
                f"{self.url}/password", json=dict(password=password)
            )
        except MetablockResponseError as exc:
            if exc.status == 401:
                return False
            else:
                raise
