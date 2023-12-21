from typing import Optional, List
from pydantic import ConfigDict, EmailStr, field_validator

from app.domain.shared.enum import UserRole, UserStatus
from app.domain.shared.entity import BaseEntity, IDModelMixin, DateTimeModelMixin, Pagination


def transform_email(email: str) -> str:
    return email.lower()


class UserBase(BaseEntity):
    email: EmailStr
    status: UserStatus = UserStatus.INACTIVE
    role: UserRole = UserRole.USER
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    # https://docs.pydantic.dev/2.4/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)

    hashed_password: Optional[str]

    def disabled(self):
        """
        Check user validity
        :return:
        """
        return self.status is UserStatus.INACTIVE.value or self.status is UserStatus.DELETED.value

    def is_user(self):
        return self.role == UserRole.USER

    def is_administrator(self):
        return self.role == UserRole.ADMIN


class UserInCreate(BaseEntity):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    role: UserRole = UserRole.USER
    _extract_email = field_validator("email", mode="before")(transform_email)


class User(UserBase):
    """
    User domain entity
    """

    id: str


class UserInUpdate(BaseEntity):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: UserStatus = UserStatus.INACTIVE
    role: UserRole = UserRole.USER
