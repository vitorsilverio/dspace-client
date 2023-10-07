from datetime import datetime
from enum import StrEnum
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
    confidence: Optional[int] = None
    place: Optional[int] = None


class PatchOperation(StrEnum):
    ADD = "add"
    MOVE = "move"
    REMOVE = "remove"
    REPLACE = "replace"


class MetadataPatch(BaseModel):
    op: PatchOperation
    path: str
    value: Optional[list[Metadata] | Metadata | str] = None
    from_field: Optional[str] = Field(alias="from", default=None)


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
    metadata: Optional[dict[str, list[Metadata]]] = None
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


class DSpaceEPersonGroup(DSpaceObject):
    permanent: bool


class DSpaceResourcePolicy(DSpaceObject):
    type: Optional[str] = None
    policyType: Optional[str] = None
    description: Optional[str] = None
    action: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None


class DSpaceEPerson(DSpaceObject):
    lastActive: datetime
    canLogin: bool
    email: str
    requireCertificate: bool
    selfRegistered: bool
    netid: Optional[str] = None


class DSpaceObjectList(BaseModel):
    communities: Optional[list[DSpaceCommunity]] = None
    collections: Optional[list[DSpaceCollection]] = None
    items: Optional[list[DSpaceItem]] = None
    groups: Optional[list[DSpaceEPersonGroup]] = None
    epersons: Optional[list[DSpaceEPerson]] = None
    bundles: Optional[list[DSpaceObject]] = None
    resourcepolicies: Optional[list[DSpaceObject]] = None


class DSpacePageDetail(BaseModel):
    size: int
    totalElements: int
    totalPages: int
    number: int


class DSpaceResponsePage(BaseModel):
    embedded: Optional[DSpaceObjectList] = Field(alias="_embedded", default=None)
    links: dict[str, Link] = Field(alias="_links")
    page: DSpacePageDetail


class EndpointGroup(StrEnum):
    ADMIN = "adminGroup"
    SUBMITTERS = "submittersGroup"
    ITEMREAD = "itemReadGroup"
    BITSTREAMREAD = "bitstreamReadGroup"
    WORKFLOW_REVIEWER = "workflowGroups/reviewer"
    WORKFLOW_REVIEWMANAGERS = "workflowGroups/reviewmanagers"
    WORKFLOW_EDITOR = "workflowGroups/editor"
    WORKFLOW_FINALEDITOR = "workflowGroups/finaleditor"
