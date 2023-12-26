from fastapi import Depends
from typing import Optional
from app.shared import request_object, response_object, use_case
from app.domain.category.entity import Category, CategoryInDB
from app.infra.category.category_repository import CategoryRepository
from app.infra.database.models.category import Category as CategoryModel


class GetCategoryRequestObject(request_object.ValidRequestObject):
    def __init__(self, category_id: str):
        self.category_id = category_id

    @classmethod
    def builder(cls, category_id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return GetCategoryRequestObject(category_id=category_id)


class GetCategoryUseCase(use_case.UseCase):
    def __init__(self, category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: GetCategoryRequestObject):
        category: Optional[CategoryModel] = self.category_repository.get_by_id(id=req_object.category_id)
        if not category:
            return response_object.ResponseFailure.build_not_found_error(message="Category does not exist.")

        return Category(**CategoryInDB.model_validate(category).model_dump())
