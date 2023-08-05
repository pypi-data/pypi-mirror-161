import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

from .utils import as_dict, as_params

if TYPE_CHECKING:  # pragma: no cover
    from .client import Metablock


class MetablockError(Exception):
    pass


class MetablockResponseError(MetablockError):
    def __init__(self, response, message=""):
        self.response = response
        self.message = as_dict(message, "message")
        self.message["request_url"] = str(response.url)
        self.message["request_method"] = response.method
        self.message["response_status"] = response.status

    @property
    def status(self):
        return self.response.status

    def __str__(self):
        return json.dumps(self.message, indent=4)


class HttpComponent(ABC):
    @abstractmethod
    def execute(self, url: str, *, method: str = "", **kwargs) -> Any:
        """Execute Http request"""

    async def get(self, url: str, **kwargs) -> Any:
        kwargs["method"] = "GET"
        return await self.execute(url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Any:
        kwargs["method"] = "PATCH"
        return await self.execute(url, **kwargs)

    async def post(self, url: str, **kwargs) -> Any:
        kwargs["method"] = "POST"
        return await self.execute(url, **kwargs)

    async def put(self, url: str, **kwargs) -> Any:
        kwargs["method"] = "PUT"
        return await self.execute(url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Any:
        kwargs["method"] = "DELETE"
        return await self.execute(url, **kwargs)


class MetablockEntity(HttpComponent):
    """A Metablock entity"""

    __slots__ = ("root", "data")

    def __init__(self, root: "CrudComponent", data: Dict) -> None:
        self.root: CrudComponent = root
        self.data: Dict = data

    def __repr__(self) -> str:
        return repr(self.data)

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, item: str) -> Any:
        return self.data[item]

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.data == other.data

    @property
    def cli(self) -> "Metablock":
        return self.root.cli

    @property
    def id(self) -> "str":
        return self.data.get("id", "")

    @property
    def name(self):
        return self.data.get("name", "")

    @property
    def url(self):
        return "%s/%s" % (self.root.url, self.id)

    def execute(self, url, **params):
        return self.cli.execute(url, **params)

    def nice(self) -> str:
        return json.dumps(self.data, indent=4)


class Component:
    __slots__ = ("root", "name")

    def __init__(
        self, root: Union["Metablock", MetablockEntity], name: str = ""
    ) -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self):
        return self.root.cli

    @property
    def url(self) -> str:
        return f"{self.cli.url}/{self.name}"


class CrudComponent(HttpComponent):
    Entity = MetablockEntity
    __slots__ = ("root", "name")

    def __init__(
        self, root: Union["Metablock", MetablockEntity], name: str = ""
    ) -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self):
        return self.root.cli

    @property
    def url(self) -> str:
        return f"{self.cli.url}/{self.name}"

    @property
    def is_entity(self) -> bool:
        return isinstance(self.root, MetablockEntity)

    def execute(self, url: str, **kwargs) -> Any:
        return self.root.execute(url, **kwargs)

    async def paginate(self, **params):
        url = self.list_create_url()
        next_ = url
        params = as_params(**params)
        while next_:
            if not next_.startswith(url):
                next_ = f'{url}?{next_.split("?")[1]}'
            data = await self.execute(next_, params=params)
            next_ = data.get("next")
            for d in data["data"]:
                yield self.wrap(d)

    def get_list(self, **params):
        url = self.list_create_url()
        return self.execute(url, params=as_params(**params), wrap=self.wrap_list)

    async def get_full_list(self, **params):
        return [d async for d in self.paginate(**params)]

    def get(self, id_, callback=None):
        url = f"{self.url}/{id_}"
        return self.execute(url, callback=callback, wrap=self.wrap)

    def has(self, id_):
        url = f"{self.url}/{id_}"
        return self.get(url, callback=self.head)

    def create(self, callback=None, **params):
        url = self.list_create_url()
        return self.post(url, json=params, callback=callback, wrap=self.wrap)

    def update(self, id_, callback=None, **params):
        url = f"{self.url}/{id_}"
        return self.patch(url, json=params, callback=callback, wrap=self.wrap)

    def upsert(self, callback=None, **params):
        return self.put(self.url, json=params, callback=callback, wrap=self.wrap)

    def delete(self, id_, callback=None):
        return self.cli.delete(f"{self.url}/{id_}", callback=callback)

    async def delete_all(self) -> int:
        n = 0
        async for entity in self.paginate():
            await self.delete(entity.id)
            n += 1
        return n

    async def head(self, response):
        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:  # pragma: no cover
            raise MetablockResponseError(response)

    def wrap(self, data):
        return self.Entity(self, data)

    def entity(self, **data):
        return self.Entity(self, data)

    def wrap_list(self, data):
        return [self.wrap(d) for d in data]

    def list_create_url(self) -> str:
        if self.is_entity:
            return f"{self.root.url}/{self.name}"
        else:
            return self.url
