from typing import Optional
from fastapi import Depends
from app.shared import request_object, response_object, use_case
from app.infra.database.models.category import Category as CategoryModel
from app.infra.category.category_repository import CategoryRepository


class DeleteCategoryRequestObject(request_object.ValidRequestObject):
    def __init__(self, id: str):
        self.id = id

    @classmethod
    def builder(cls, id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return DeleteCategoryRequestObject(id=id)


class DeleteTransactionUseCase(use_case.UseCase):
    def __init__(self, category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: DeleteCategoryRequestObject):
        transaction: Optional[CategoryModel] = self.category_repository.get_by_id(id=req_object.id)
        if not transaction:
            return response_object.ResponseFailure.build_not_found_error(message="Category does not exist.")
        self.category_repository.delete(req_object.id)
        return {"success": True}
