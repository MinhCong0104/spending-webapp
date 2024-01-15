from datetime import datetime, date as Date
from typing import Optional, List, Union
from pydantic import ConfigDict
from app.domain.shared.entity import BaseEntity, IDModelMixin, DateTimeModelMixin, Pagination
from app.domain.user.field import PydanticUserType
from app.domain.category.field import PydanticCategoryType
from app.domain.shared.enum import Type


class TransactionBase(BaseEntity):
    date: Union[datetime, Date]
    amount: float
    note: Optional[str] = None
    type: Type


class TransactionInDB(IDModelMixin, DateTimeModelMixin, TransactionBase):
    # https://docs.pydantic.dev/2.4/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)
    user: PydanticUserType
    category: PydanticCategoryType


class TransactionInCreate(BaseEntity):
    name: str
    type: Type
    amount: float
    note: Optional[str] = None
    # category: str
    date: str


class TransactionInUpdate(BaseEntity):
    date: Optional[Union[datetime, Date]]
    amount: Optional[float] = None
    note: Optional[str] = None
    type: Optional[Type] = None


class Transaction(TransactionBase):
    """
    Transaction domain entity
    """

    id: str
