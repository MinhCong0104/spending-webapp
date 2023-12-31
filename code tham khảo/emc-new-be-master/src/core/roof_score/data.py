from typing import Dict, Optional
from pydantic import BaseModel, Field, NonNegativeFloat, conlist, constr
from bson import ObjectId
from src.infra.database.helper import PyObjectId
from datetime import datetime
from enum import Enum

# env_classes = ['background', 'car', 'grass', 'road', 'roof', 'tree', 'walkway']
class EnvClass(str, Enum):
    Background = 'background'
    Car = 'car'
    Trees = 'tree'
    Roof = 'roof'
    Grass = 'grass'
    Walkway = 'walkway'
    Road = 'road'

# defects_classes = ['background', 'ballast_displacement', 'blocked_drain', 'corrosion', 'damaged_walkways',
                    # 'debris', 'mold_growing_on_roof', 'overhanging_vegetation', 'patching', 'ponding',
                    # 'steps_without_adequate_contrast', 'wrinkled_membrane']
class DefectClass(str, Enum):
    Background = 'background'
    Ponding = 'ponding'
    BallastDisplacement = 'ballast_displacement'
    RoofMold = 'mold_growing_on_roof'
    Corrosion = 'corrosion'
    WrinkledMembrane = 'wrinkled_membrane'
    WalkwayCrack = 'walkway_crack'
    Patching = 'patching'
    Debris = 'debris'
    LowStepContrast = 'LowStepContrast'
    OverhangingVegetation = 'overhanging_vegetation'
    BLockedDrain = 'blocked_drain'
    DamagedWalkways = 'damaged_walkways'
    StepsWithoutAdequateContrast = 'steps_without_adequate_contrast'

class ImageType(str, Enum):
    NoML = 'no_ml'
    MLProcessed = 'ml_processed'


class DefectThresholdSettings(BaseModel):
    general_threshold: Optional[float] # 0..1
    defect_type_threshold: Optional[Dict[DefectClass, float]] # 0..1

    class Config:
        arbitrary_types_allowed = True


class DefectPolyGon(BaseModel):
    points: Optional[list[conlist(int, min_items=2)]] = None
    defect_class: DefectClass
    surface_class: Optional[str] # TODO: correct env class later when db data fixed
    confidence_score: float = 0.9 # 0..1 # TODO: use default value for now until all db data is updated

    class Config:
        arbitrary_types_allowed = True

class Defect(BaseModel):
    polygons: list[DefectPolyGon] = []

    class Config:
        arbitrary_types_allowed = True


class EnvironmentContour(BaseModel):
    env_class: EnvClass
    points: Optional[list[conlist(int, min_items=2)]] = None

    class Config:
        arbitrary_types_allowed = True
        

class MissionImageUpdate(BaseModel):
    img_name: str
    defects: Defect
    roof_contours: Optional[list]
    env_contours: Optional[list[EnvironmentContour]]
    threshold_settings: Optional[DefectThresholdSettings]
    score: NonNegativeFloat

    class Config:
        arbitrary_types_allowed = True


class MissionImageScoreUpdate(BaseModel):
    img_name: str
    defects: Defect
    roof_contours: Optional[list] = None
    env_contours: Optional[list[EnvironmentContour]] = None
    threshold_settings: Optional[DefectThresholdSettings]

    class Config:
        arbitrary_types_allowed = True


class MissionScoreUpdate(BaseModel):
    image_updates: list[MissionImageUpdate]
    project_threshold_settings: Optional[DefectThresholdSettings]
    avg_score: NonNegativeFloat
    time: datetime

    class Config:
        arbitrary_types_allowed = True

class MissionScoreUpdatePayload(BaseModel):
    image_updates: Optional[list[MissionImageScoreUpdate]] = []
    project_threshold_settings: Optional[DefectThresholdSettings]

    class Config:
        arbitrary_types_allowed = True

class Task(BaseModel):
    id: str
    status: Optional[str]

class MissionScore(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mission_id: Optional[str]
    avg_score: Optional[NonNegativeFloat]
    updates: list[MissionScoreUpdate] = []
    project_threshold_settings: Optional[DefectThresholdSettings]
    emc_rcif: Optional[str]
    submitted_date: Optional[datetime]
    task_updating: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        # schema_extra = {
        #     "example": {
        #         "name": "Jane Doe",
        #         "email": "jdoe@example.com",
        #         "course": "Experiments, Science, and Fashion in Nanophotonics",
        #         "gpa": "3.0",
        #     }
        # }


class MissionScoreCreate(BaseModel):
    mission_id: str
    avg_score: NonNegativeFloat
    emc_rcif: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class RoofMask(BaseModel):
    shape: conlist(int, min_items=2)
    dtype: constr(regex=r'^((u?int)|(u?short)|(float)|(double)|(long))[\w\d]*$') # numpy data types
    contour: list = []

    class Config:
        arbitrary_types_allowed = True


class MissionImage(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    mission_id: str
    img_name: str
    roof_mask: Optional[RoofMask]
    env_contours: list[EnvironmentContour] = []
    defects: Optional[Defect]
    threshold_settings: Optional[DefectThresholdSettings]
    score: NonNegativeFloat
    emc_rcif: Optional[str]
    img_type: Optional[ImageType]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MissionImageCreate(BaseModel):
    img_name: str
    roof_mask: RoofMask
    env_contours: list[EnvironmentContour] = []
    defects: Defect
    score: NonNegativeFloat
    mission_id: Optional[str]
    emc_rcif: Optional[str]

    class Config:
        arbitrary_types_allowed = True

class MissionUpdateScoreStatus(BaseModel):
    version_id: str
    update_status: str
    user_id: str