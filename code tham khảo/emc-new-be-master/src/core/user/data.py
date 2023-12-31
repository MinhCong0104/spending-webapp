from typing import Dict, Optional, List
from pydantic import BaseModel, Field, NonNegativeFloat
from bson import ObjectId
from src.infra.database.helper import PyObjectId
from enum import Enum
from fastapi import Form, UploadFile, File
from dataclasses import dataclass, field

class VDAUserRole(str, Enum):
    Admin = 'admin'
    SuperAdmin = 'superadmin'
    User = 'user'
    Automation = 'automation'

class Center(BaseModel):
    lat: NonNegativeFloat
    lng: NonNegativeFloat


class Address(BaseModel):
    address: str
    center: Optional[list[Center]] = None
    zoom: NonNegativeFloat


class Company(BaseModel):
    _id: str
    name: str

class TemporaryPassword(BaseModel):
    temporary_password: Optional[str]

@dataclass
class UserCreateUpdate:
    email: Optional[str] = Form(None)
    password: Optional[str] = Form(None)
    newPassword: Optional[str] = Form(None)
    firstName: Optional[str] = Form(None)
    lastName: Optional[str] = Form(None)
    username: Optional[str] = Form(None)
    birth: Optional[str] = Form(None)
    phone: Optional[str] = Form(None)
    address: Optional[str] = Form(None)
    assign: Optional[str] = Form(None)
    status: Optional[str] = Form(None)
    role: Optional[str] = Form(None)
    company: Optional[str] = Form(None)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ListQueryOptions(BaseModel):
    email: str
    maxResults: Optional[NonNegativeFloat]
    nextToken: Optional[str]

class UserGroup(str, Enum):
    Admin = 'Admin'
    SuperAdmin = 'SuperAdmin'
    User = 'User'