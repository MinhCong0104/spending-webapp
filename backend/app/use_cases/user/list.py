import math
from typing import Optional, List
from fastapi import Depends
from app.shared import request_object, use_case
from app.domain.user.entity import User, UserInDB, ManyUsersInResponse
from app.domain.shared.entity import Pagination
from app.infra.database.models.user import User as UserModel
from app.infra.user.user_repository import UserRepository
from app.domain.shared.enum import UserRole


class ListUsersRequestObject(request_object.ValidRequestObject):
    def __init__(
        self,
        current_user: User,
        role: UserRole,
        email: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 100,
    ):
        self.current_user = current_user
        self.role = role
        self.email = email
        self.page_index = page_index
        self.page_size = page_size

    @classmethod
    def builder(
        cls,
        current_user: User,
        role: UserRole = UserRole.USER,
        email: Optional[str] = None,
        page_index: int = 1,
        page_size: int = 100,
    ) -> request_object.RequestObject:
        return ListUsersRequestObject(
            current_user=current_user, role=role, email=email, page_index=page_index, page_size=page_size
        )


class ListUsersUseCase(use_case.UseCase):
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def process_request(self, req_object: ListUsersRequestObject):

        users: List[UserModel] = self.user_repository.list(
            role=req_object.role,
            email=req_object.email,
            page_index=req_object.page_index,
            page_size=req_object.page_size,
        )

        conditions = {"role": req_object.role.value}
        if req_object.email:
            conditions = {**conditions, "email": {"$regex": ".*" + req_object.email + ".*"}}
        total = self.user_repository.count(conditions)
        data = [User(**UserInDB.model_validate(model).model_dump()) for model in users]
        return data
