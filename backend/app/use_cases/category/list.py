import math
from typing import Optional, List
from fastapi import Depends
from app.shared import request_object, use_case
from app.domain.user.entity import User
from app.infra.database.models.category import Category as CategoryModel
from app.infra.category.category_repository import CategoryRepository
from app.domain.shared.enum import Type


class ListCategoriesRequestObject(request_object.ValidRequestObject):
    def __init__(
        self,
        current_user: User,
        name: str,
        type: Type,
        note: str,
    ):
        self.current_user = current_user
        self.name = name
        self.type = type
        self.note = note

    @classmethod
    def builder(
        cls,
        current_user: User,
        type: Optional[Type] = None,
        name: Optional[str] = None,
        note: Optional[str] = None,
    ) -> request_object.RequestObject:
        return ListCategoriesRequestObject(current_user=current_user, name=name, type=type, note=note)


class ListCategoriesUseCase(use_case.UseCase):
    def __init__(self, category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: ListUsersRequestObject):

        categories: List[CategoryModel] = self.category_repository.list(
            user=req_object.current_user,
            email=req_object.email,
            page_index=req_object.page_index,
            page_size=req_object.page_size,
        )

        conditions = {"role": req_object.role.value}
        if req_object.email:
            conditions = {**conditions, "email": {"$regex": ".*" + req_object.email + ".*"}}
        total = self.user_repository.count(conditions)
        data = [User(**UserInDB.model_validate(model).model_dump()) for model in users]
        return ManyUsersInResponse(
            pagination=Pagination(
                total=total, page_index=req_object.page_index, total_pages=math.ceil(total / req_object.page_size)
            ),
            data=data,
        )
