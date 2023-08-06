from typing import Dict

from .components import CrudComponent, MetablockEntity
from .extensions import Extensions, Plugins
from .spaces import Spaces


class OrgSpaces(Spaces):
    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)


class OrgExtensions(Extensions):
    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)


class OrgPlugins(Plugins):
    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)


class Org(MetablockEntity):
    """Object representing an Organization"""

    @property
    def name(self):
        return self.data.get("short_name", "")

    @property
    def spaces(self) -> OrgSpaces:
        return OrgSpaces(self, "spaces")

    @property
    def plugins(self) -> OrgPlugins:
        return OrgPlugins(self, "plugins")

    @property
    def extensions(self) -> OrgExtensions:
        return OrgExtensions(self, "extensions")

    @property
    def members(self) -> "Members":
        return Members(self)

    @property
    def roles(self) -> "Roles":
        return Roles(self)

    async def add_info(self, **data) -> Dict:
        return await self.patch(f"{self.url}/info", json=data, wrap=self.root.wrap)


class Member(MetablockEntity):
    """Object representing a organization member"""


class Role(MetablockEntity):
    """Object representing a organization role"""


class Members(CrudComponent):
    """Metablock organizations"""

    Entity = Member

    @property
    def url(self) -> str:
        return f"{self.root.url}/{self.name}"


class Roles(CrudComponent):
    """Metablock organizations"""

    Entity = Role

    @property
    def url(self) -> str:
        return f"{self.root.url}/{self.name}"


class Orgs(CrudComponent):
    """Metablock organizations"""

    Entity = Org
