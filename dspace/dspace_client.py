import datetime
import logging
import tomllib
import urllib.parse
from typing import TypeVar

import jwt
from httpx import Client, Response
from pydantic import BaseModel

from dspace.exceptions import DSpaceAuthenticationError, DSpaceSessionExpiredError, DSpaceApiError
from dspace.dspace_objects import DSpaceApiObject, DSpaceResponsePage, DSpaceError, Link, DSpaceItemTemplate, \
    DSpaceCollection, MetadataPatch, DSpaceEPersonGroup

handler = logging.StreamHandler()
log = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

T = TypeVar("T")


class DSpaceClient:

    def __init__(self, server: str):
        self.base_url = server
        self.client = Client()
        self.__update_client_info()
        self.api_info = self.api()
        self.__error = None

    def login(self, username: str, password: str):
        response = self.client.post(urllib.parse.urljoin(self.base_url, "api/authn/login"), data={
            "user": username,
            "password": password
        })
        if response.status_code != 200:
            raise DSpaceAuthenticationError()
        self.client.headers.update({"Authorization": response.headers.get("Authorization")})
        self.__post_processing_response(response)

    def __update_client_info(self):
        with open("pyproject.toml", "rb") as f:
            toml = tomllib.load(f)
            project_info = toml["tool"]["poetry"]
            self.client.headers.update({"User-Agent": f"{project_info['name']} {project_info['version']}"})

    def __save_xsrf_token(self, response: Response):
        xsrf_cookie = response.cookies.get("DSPACE-XSRF-COOKIE")
        if xsrf_cookie:
            self.client.headers.update({"X-XSRF-TOKEN": xsrf_cookie})

    def __refresh_token(self):
        auth = self.client.headers.get("Authorization")
        if not auth:
            return
        jwt_token = jwt.decode(auth[len("Bearer "):], options={"verify_signature": False})
        exp = datetime.datetime.fromtimestamp(jwt_token["exp"])

        now = datetime.datetime.now()
        if now > exp:
            log.error("Session Expired: Cannot refresh token")
            raise DSpaceSessionExpiredError()
        if now + datetime.timedelta(minutes=5) > exp:
            response = self.client.post(urllib.parse.urljoin(self.base_url, "api/authn/login"))
            self.client.headers.update({"Authorization": response.headers.get("Authorization")})
            self.__post_processing_response(response)

    def __post_processing_response(self, response: Response):
        if response.status_code >= 400:
            error = DSpaceError(**response.json())
            log.error(error)
            self.__error = error
            raise DSpaceApiError(error)
        self.__save_xsrf_token(response)
        self.__refresh_token()
        self.__error = None

    def api(self) -> DSpaceApiObject:
        response = self.client.get(urllib.parse.urljoin(self.base_url, "api"))
        self.__post_processing_response(response)
        return DSpaceApiObject(**response.json())

    def __fetch_dspace_page(self, path: str, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        response = self.client.get(urllib.parse.urljoin(self.base_url, path),
                                   params={"size": size, "page": page})
        self.__post_processing_response(response)
        return DSpaceResponsePage(**response.json())

    def __fetch_object(self, object_type: type[T], path: str) -> T:
        response = self.client.get(urllib.parse.urljoin(self.base_url, path))
        self.__post_processing_response(response)
        return object_type(**response.json())

    def __create_object(self, object_type: type[T], path: str, obj: BaseModel | None = None) -> T:
        if obj:
            object_json = obj.model_dump(exclude_none=True)
        else:
            object_json = {}
        response = self.client.post(urllib.parse.urljoin(self.base_url, path),
                                    json=object_json)
        self.__post_processing_response(response)
        return object_type(**response.json())

    def __update_metadata(self, object_type: type[T], path: str, metadata_patches: list[MetadataPatch]) -> T:
        response = self.client.patch(
            urllib.parse.urljoin(self.base_url, path),
            json=[patch.model_dump(exclude_none=True) for patch in metadata_patches])
        self.__post_processing_response(response)
        return object_type(**response.json())

    def get_communities(self, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        return self.__fetch_dspace_page("api/core/communities", page, size)

    def get_collections(self, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        return self.__fetch_dspace_page("api/core/collections", page, size)

    def get_items(self, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        return self.__fetch_dspace_page("api/core/items", page, size)

    def get_eperson_groups(self, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        return self.__fetch_dspace_page("api/eperson/groups", page, size)

    def get_epeople(self, page: int = 0, size: int = 20) -> DSpaceResponsePage:
        return self.__fetch_dspace_page("/api/eperson/epersons", page, size)

    def get_item_template(self, uuid: str) -> DSpaceItemTemplate:
        return self.__fetch_object(DSpaceItemTemplate, f"api/core/itemtemplates/{uuid}")

    def get_by_link(self, object_type: type[T], link: Link) -> T:
        response = self.client.get(link.href)
        self.__post_processing_response(response)
        return object_type(**response.json())

    def create_item_template(self, collection: DSpaceCollection | str) -> DSpaceItemTemplate:
        if isinstance(collection, DSpaceCollection):
            collection = collection.uuid
        return self.__create_object(DSpaceItemTemplate, f"api/core/collections/{collection}/itemtemplate")

    def create_collection_role(self, collection: DSpaceCollection | str, role_endpoint: str) -> DSpaceEPersonGroup:
        if isinstance(collection, DSpaceCollection):
            collection = collection.uuid
        return self.__create_object(DSpaceEPersonGroup, f"api/core/collections/{collection}/{role_endpoint}")

    def update_item_template(self, item_template: DSpaceItemTemplate,
                             metadata_patches: list[MetadataPatch]) -> DSpaceItemTemplate:
        return self.__update_metadata(DSpaceItemTemplate, f"api/core/itemtemplates/{item_template.uuid}",
                                      metadata_patches)

    def update_collection_metadata(self, collection: DSpaceCollection, metadata_patches: list[MetadataPatch]):
        return self.__update_metadata(DSpaceCollection, f"api/core/collections/{collection.id}", metadata_patches)

    def delete_item_template(self, uuid: str) -> None:
        response = self.client.delete(urllib.parse.urljoin(self.base_url, f"api/core/itemtemplates/{uuid}"))
        self.__post_processing_response(response)

    def get_last_execution_error(self) -> DSpaceError:
        return self.__error
