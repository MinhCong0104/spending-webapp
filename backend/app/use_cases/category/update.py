from typing import Optional
from fastapi import Depends
from app.infra.database.models.category import Category as CategoryModel
from app.shared import request_object, use_case, response_object

from app.domain.category.entity import CategoryInUpdate, CategoryInDB, Category
from app.infra.category.category_repository import CategoryRepository


class UpdateCategoryRequestObject(request_object.ValidRequestObject):
    def __init__(self, id: str, obj_in: CategoryInUpdate) -> None:
        self.id = id
        self.obj_in = obj_in

    @classmethod
    def builder(cls, id: str, payload: Optional[CategoryInUpdate]) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if id is None:
            invalid_req.add_error("id", "Invalid category id")

        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return UpdateCategoryRequestObject(id=id, obj_in=payload)


class UpdateCategoryUseCase(use_case.UseCase):
    def __init__(self, category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: UpdateCategoryRequestObject):
        category: Optional[CategoryModel] = self.category_repository.get_by_id(req_object.id)
        if not category:
            return response_object.ResponseFailure.build_not_found_error("Category does not exist")

        self.category_repository.update(id=category.id, data=req_object.obj_in)
        category.reload()
        return Category(**CategoryInDB.model_validate(category).model_dump())
