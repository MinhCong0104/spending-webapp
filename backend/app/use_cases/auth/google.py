import httpx
from typing import Optional
from fastapi import Depends, HTTPException
from app.domain.user.entity import User, UserInDB, UserInCreate
from app.domain.auth.entity import AuthInfo, AuthInfoInResponse, Token
from app.shared import response_object, use_case, request_object
from app.infra.user.user_repository import UserRepository
from app.infra.security.security_service import (
    SecurityService,
    create_access_token,
    get_password_hash,
    generate_random_password,
)
from app.domain.shared.enum import AuthGrantType, UserRole
from app.config import settings


class GoogleRequestObject(request_object.ValidRequestObject):
    def __init__(self, id_token: str):
        self.id_token = id_token

    @classmethod
    def builder(cls, id_token: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id_token:
            invalid_req.add_error("id_token", "Invalid")

        if invalid_req.has_errors():
            return invalid_req
        return GoogleRequestObject(id_token=id_token)


class GoogleAuthUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService),
    ):
        self.user_repository = user_repository
        self.security_service = security_service

    def fetch_user_info(self, id_token: str) -> Optional[AuthInfo]:
        try:
            resp = httpx.get(settings.GOOGLE_TOKEN_INFO, params={"id_token": id_token})
            resp.raise_for_status()
            return AuthInfo(**resp.json())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def process_request(self, req_object: GoogleRequestObject):
        user_data: Optional[AuthInfo] = self.fetch_user_info(id_token=req_object.id_token)
        if user_data.email is None:
            return response_object.ResponseFailure.build_parameters_error(message="Email is empty")

        user: UserInDB = self.security_service.get_user(email=user_data.email)
        if not user:
            # Create new user with email
            user_in: UserInCreate = UserInCreate(
                email=user_data.email,
                first_name=user_data.given_name,
                last_name=user_data.family_name,
                role=UserRole.ACCOUNTANT,
                avatar=user_data.picture,
            )
            obj_in: UserInDB = UserInDB(
                **user_in.model_dump(),
                hashed_password=get_password_hash(password=generate_random_password()),
            )
            user: UserInDB = self.user_repository.create(user=obj_in)

        # create access token from user data
        access_token = create_access_token(
            data={
                "sub": user.email,
                "id": str(user.id),
                "grant_type": AuthGrantType.ACCESS_TOKEN.value,
            }
        )
        return AuthInfoInResponse(
            token=Token(access_token=access_token, token_type="bearer"),
            user=User(**UserInDB.model_validate(user).model_dump()),
        )
