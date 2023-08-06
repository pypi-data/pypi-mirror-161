from typing import Dict

from aiohttp.formdata import FormData

from .components import Component, CrudComponent, MetablockEntity


# Space
class Space(MetablockEntity):
    """Object representing a space"""

    @property
    def services(self) -> "SpaceServices":
        return SpaceServices(self, "services")

    @property
    def extensions(self) -> "SpaceExtensions":
        return SpaceExtensions(self, "extensions")


class Spaces(CrudComponent):
    """Spaces"""

    Entity = Space


# Service
class Service(MetablockEntity):
    """Object representing a service"""

    @property
    def plugins(self):
        return ServicePlugins(self, "plugins")

    @property
    def deployments(self):
        return CrudComponent(self, "deployments")

    async def config(self, *, callback=None) -> Dict:
        return await self.get(f"{self.url}/config", callback=callback)

    async def ship(self, name: str, bundle: str, env="stage", *, callback=None) -> Dict:
        data = FormData()
        data.add_field("name", name)
        data.add_field("bundle", open(bundle, "rb"), filename=bundle)
        data.add_field("env", env)
        return await self.post(f"{self.url}/deployments", data=data, callback=callback)


class Services(CrudComponent):
    """Services"""

    Entity = Service


class SpaceServices(Services):
    def list_create_url(self) -> str:
        return self.parent_url


# SpaceExtension
class SpaceExtension(MetablockEntity):
    """Object representing an SpaceExtension"""


class SpaceExtensions(CrudComponent):
    Entity = SpaceExtension

    def list_create_url(self) -> str:
        return self.parent_url

    def delete_url(self, id_name: str) -> str:
        return f"{self.parent_url}/{id_name}"


# ServicePlugin


class ServicePlugin(MetablockEntity):
    """Object representing an ServicePlugin"""


class ServicePlugins(CrudComponent):
    Entity = ServicePlugin

    def list_create_url(self) -> str:
        return self.parent_url

    def delete_url(self, id_name: str) -> str:
        return f"{self.parent_url}/{id_name}"


# Domain


class Domains(Component):
    async def check(self, domain: str) -> str:
        return await self.cli.get(f"{self.url}/check/{domain}")
