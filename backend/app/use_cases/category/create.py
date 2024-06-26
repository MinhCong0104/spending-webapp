from typing import Optional
from fastapi import Depends
from app.infra.security.security_service import get_password_hash
from app.shared import request_object, use_case

from app.domain.category.entity import Category, CategoryInCreate, CategoryInDB
from app.infra.category.category_repository import CategoryRepository
from app.infra.database.models.user import User as UserModel


class CreateCategoryRequestObject(request_object.ValidRequestObject):
    def __init__(self, category_in: CategoryInCreate, current_user: UserModel) -> None:
        self.category_in = category_in
        self.current_user = current_user

    @classmethod
    def builder(cls, payload: Optional[CategoryInCreate], current_user: UserModel) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return CreateCategoryRequestObject(category_in=payload, current_user=current_user)


class CreateCategoryUseCase(use_case.UseCase):
    def __init__(self, category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: CreateCategoryRequestObject):
        category_in: CategoryInCreate = req_object.category_in
        existing_category: Optional[CategoryInDB] = self.category_repository.get_by_name(name=category_in.name)
        if existing_category:
            return Category(**existing_category.model_dump())

        obj_in: CategoryInDB = CategoryInDB(**category_in.model_dump(), user=req_object.current_user)
        category_in_db: CategoryInDB = self.category_repository.create(category=obj_in)
        return Category(**category_in_db.model_dump())
