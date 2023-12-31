from typing import Optional, Any
from pydantic import BaseModel, Field, NonNegativeFloat, conlist
from bson import ObjectId
from src.infra.database.helper import PyObjectId
from enum import Enum
from datetime import datetime
from src.core.roof_score.data import DefectClass, EnvClass
from src.core.user.data import Address, UserCreateUpdate


class Pilot(BaseModel):
    _id: str
    email: str
    firstName: str
    lastName: str


class Weather(BaseModel):
    date: str
    temp: NonNegativeFloat
    summary: str
    humidity: NonNegativeFloat


class Workflow(BaseModel):
    update_at: str
    value: str


class DataAvailable(BaseModel):
    demjpg: bool
    demtif: bool
    demtile: bool
    hdobj: bool
    geoobj: bool
    tile3d: bool
    orthojpg: bool
    orthotif: bool
    orthotile: bool
    rawimages: bool
    wireframe: bool
    userannotations: bool
    userpolygons: bool
    damage: str


class MissionVersion(BaseModel):
    _id: str
    missionname: str
    droneused: str
    droneserial: str
    location: Optional[list[Address]] = None
    pilot: Pilot
    weather: Weather
    workflow: Workflow
    dataavailable: DataAvailable
    created_at: str


class PolygonTypeClass(str, Enum):
    polygon = 'polygon'
    square = 'square'


class PolygonInfo(BaseModel):
    defect_class: DefectClass
    env_class: EnvClass
    type: PolygonTypeClass


class MissionVersionPolygon(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    versionId: str
    info: PolygonInfo
    points: Optional[list[conlist(int, min_items=2)]] = None
    is2DOriginal: bool

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MissionVersionPolygonUpdate(BaseModel):
    # _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    versionId: str
    info: PolygonInfo
    points: Optional[list[conlist(int, min_items=2)]] = None
    is2DOriginal: bool

    class Config:
        arbitrary_types_allowed = True


class MissionVersionAssign(BaseModel):
    versionId: str
    users: Optional[list]


class UserIds(BaseModel):
    add: Optional[list[str]]
    remove: Optional[list[str]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MissionRawImageFavourite(BaseModel):
    imageId: str
    versionId: Optional[str] = None
    favourite: bool


class Author(BaseModel):
    _id: str
    email: str
    firstName: str
    lastName: str


class MissionImageAnnotation(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    author: Author
    content: str
    left: NonNegativeFloat
    top: NonNegativeFloat

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MissionTilesetAnnotation(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is2DOriginal: Optional[bool]
    author: Optional[Any]
    content: str
    position: Optional[list]


class RoofTestSquareDamage(BaseModel):
    value: str
    type: str


class Info(BaseModel):
    roofTestSquareDamages: RoofTestSquareDamage
    notes: str


class Polygon(BaseModel):
    _id: Optional[str]
    fill: Optional[str]
    stroke: Optional[str]
    type: Optional[str]
    info: Info
    points: Optional[list]


class MissionImagePolygon(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    url: Optional[str]
    Polygon: Optional[list[Polygon]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Roofing(BaseModel):
    value: Optional[str]
    type: Optional[str]
    state: Optional[str]
    damageType: Optional[str]


class InfoTitleset(BaseModel):
    note: Optional[str]
    roofing: Roofing


class MissionTilesetPolygon(BaseModel):
    info: InfoTitleset
    points: Optional[list[conlist(int, min_items=2)]] = None
    is2DOriginal: Optional[bool]
    type: Optional[str]
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class MissionShare(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creator: Optional[str]
    exp: datetime
    versionId: Optional[str]
    email: Optional[str]
    onlyReport: Optional[bool]
    creatorData: Optional[UserCreateUpdate]


class ShareSendEmail(BaseModel):
    url: Optional[str]
    email: Optional[str]
    shareId: Optional[str]
