from fastapi import Depends
from typing import Optional
from app.shared import request_object, response_object, use_case
from app.domain.user.entity import User, UserInDB
from app.infra.user.user_repository import UserRepository
from app.infra.database.models.user import User as UserModel


class GetUserRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_id: str):
        self.user_id = user_id

    @classmethod
    def builder(cls, user_id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return GetUserRequestObject(user_id=user_id)


class GetUserCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: GetUserRequestObject):
        user: Optional[UserModel] = self.user_repository.get_by_id(user_id=req_object.user_id)
        if not user:
            return response_object.ResponseFailure.build_not_found_error(message="User does not exist.")

        return User(**UserInDB.model_validate(user).model_dump())
