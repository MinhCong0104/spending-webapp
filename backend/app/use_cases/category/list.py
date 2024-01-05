import math
from typing import Optional, List
from fastapi import Depends
from app.shared import request_object, use_case
from app.domain.user.entity import User
from app.domain.category.entity import Category, CategoryInDB
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

    def process_request(self, req_object: ListCategoriesRequestObject):

        categories: List[CategoryModel] = self.category_repository.list(
            user=req_object.current_user,
            type=req_object.type,
            name=req_object.name,
            note=req_object.note,
        )

        data = [Category(**CategoryInDB.model_validate(model).model_dump()) for model in categories]
        return data
