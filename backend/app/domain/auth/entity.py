from typing import Optional
from pydantic import BaseModel, EmailStr
from app.domain.shared.entity import BaseEntity
from app.domain.shared.enum import AuthGrantType
from app.domain.user.entity import User


class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str = None
    id: str = None
    grant_type: Optional[AuthGrantType] = AuthGrantType.ACCESS_TOKEN


class AuthInfo(BaseEntity):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None


class UserInLogin(AuthInfo):
    password: Optional[str] = None


class AuthInfoInResponse(BaseEntity):
    token: Token
    user: User
