from typing import Optional
from fastapi import Depends
from app.infra.security.security_service import get_password_hash
from app.shared import request_object, use_case

from app.domain.user.entity import User, UserInCreate, UserInDB
from app.infra.user.user_repository import UserRepository


class CreateUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_in: UserInCreate = None) -> None:
        self.user_in = user_in

    @classmethod
    def builder(cls, payload: Optional[UserInCreate] = None) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if not payload.email:
            invalid_req.add_error("payload.email", "Invalid email")

        if invalid_req.has_errors():
            return invalid_req

        return CreateUserRequestObject(user_in=payload)


class CreateUserUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: CreateUserRequestObject):
        user_in: UserInCreate = req_object.user_in
        existing_user: Optional[UserInDB] = self.user_repository.get_by_email(email=user_in.email)
        if existing_user:
            return User(**existing_user.model_dump())

        obj_in: UserInDB = UserInDB(
            **user_in.model_dump(exclude={"password"}), hashed_password=get_password_hash(password=user_in.password)
        )
        user_in_db: UserInDB = self.user_repository.create(user=obj_in)
        return User(**user_in_db.model_dump())
