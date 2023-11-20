from fastapi import Depends
from pydantic import ValidationError
from app.domain.user.entity import User, UserInDB
from app.shared import request_object, response_object, use_case
from app.domain.auth.entity import AuthInfoInResponse, Token, UserInLogin
from app.infra.user.user_repository import UserRepository
from app.infra.security.security_service import (
    SecurityService,
    create_access_token,
)
from app.infra.database.models.user import User as UserModel
from app.domain.shared.enum import AuthGrantType


class LoginRequestObject(request_object.ValidRequestObject):
    def __init__(self, login_info: UserInLogin):
        self.login_info = login_info

    @classmethod
    def builder(cls, data: dict) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not data:
            invalid_req.add_error("data", "Invalid")

        try:
            login_info = UserInLogin(**data)
        except ValidationError as e:
            invalid_req.add_error_map(e.errors())

        if invalid_req.has_errors():
            return invalid_req

        return LoginRequestObject(login_info=login_info)


class LoginUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService),
    ):
        self.user_repository = user_repository
        self.security_service = security_service

    def process_request(self, req_object: LoginRequestObject):
        # authenticate user with auth info
        user: UserModel = self.security_service.authenticate_user(
            email=req_object.login_info.email,
            password=req_object.login_info.password,
        )
        if not user:
            return response_object.ResponseFailure.build_parameters_error(message="Incorrect email or password")

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
