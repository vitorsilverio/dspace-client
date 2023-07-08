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
    language: str | None
    authority: str | None
    confidence: int
    place: int


class DSpaceApiObject(BaseModel):
    dspaceUI: str
    dspaceName: str
    dspaceServer: str
    dspaceVersion: str
    type: str
    links: dict[str, Link] = Field(alias="_links")


class DSpaceObject(BaseModel):
    id: int | str
    uuid: Optional[str]
    name: str
    handle: Optional[str]
    type: str
    metadata: dict[str, list[Metadata]]
    links: dict[str, Link] = Field(alias="_links")


class DSpaceCommunity(DSpaceObject):
    archivedItemsCount: int


class DSpaceItem(DSpaceObject):
    inArchive: bool
    discoverable: bool
    withdrawn: bool
    lastModified: datetime
    entityType: str | None


class DSpaceObjectList(BaseModel):
    communities: Optional[list[DSpaceCommunity]] = None
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
