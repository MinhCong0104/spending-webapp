from datetime import datetime, date as Date
from typing import Optional, List, Union
from pydantic import ConfigDict
from app.domain.shared.entity import BaseEntity, IDModelMixin, DateTimeModelMixin, Pagination
from app.domain.user.field import PydanticUserType


class CategoryBase(BaseEntity):
    name: str
    type: str
    note: Optional[str] = None


class CategoryInDB(IDModelMixin, DateTimeModelMixin, CategoryBase):
    # https://docs.pydantic.dev/2.4/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)
    user: PydanticUserType


class CategoryInCreate(BaseEntity):
    name: str
    type: str
    note: Optional[str] = None


class CategoryInUpdate(BaseEntity):
    name: Optional[str] = None
    type: Optional[str] = None
    note: Optional[str] = None


class Category(CategoryBase):
    """
    Journal domain entity
    """

    id: str
    created_at: datetime
