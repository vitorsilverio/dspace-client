from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DSpaceError(BaseModel):
    timestamp: datetime
    status: int
    error: str
    message: str
    path: str


class Link(BaseModel):
    href: str


class Metadata(BaseModel):
    value: str
    language: Optional[str] = None
    authority: Optional[str] = None
    confidence: int = -1
    place: int = 0


class DSpaceApiObject(BaseModel):
    dspaceUI: str
    dspaceName: str
    dspaceServer: str
    dspaceVersion: str
    type: str
    links: dict[str, Link] = Field(alias="_links")


class DSpaceObject(BaseModel):
    type: str
    id: Optional[int | str] = None
    metadata: dict[str, list[Metadata]]
    uuid: Optional[str] = None
    name: Optional[str] = None
    handle: Optional[str] = None
    links: Optional[dict[str, Link | list[Link]]] = Field(alias="_links", default=None)


class DSpaceCommunity(DSpaceObject):
    archivedItemsCount: int

class DSpaceCollection(DSpaceObject):
    archivedItemsCount: int


class DSpaceItem(DSpaceObject):
    inArchive: bool
    discoverable: bool
    withdrawn: bool
    lastModified: Optional[datetime] = None
    entityType: Optional[str] = None

class DSpaceItemTemplate(DSpaceObject):
    lastModified: Optional[datetime] = None


class DSpaceObjectList(BaseModel):
    communities: Optional[list[DSpaceCommunity]] = None
    collections: Optional[list[DSpaceCollection]] = None
    items: Optional[list[DSpaceItem]] = None


class DSpacePageDetail(BaseModel):
    size: int
    totalElements: int
    totalPages: int
    number: int


class DSpaceResponsePage(BaseModel):
    embedded: DSpaceObjectList = Field(alias="_embedded")
    links: dict[str, Link] = Field(alias="_links")
    page: DSpacePageDetail
