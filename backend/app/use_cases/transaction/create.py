from typing import Optional
from fastapi import Depends
from app.shared import request_object, use_case

from app.domain.transaction.entity import Transaction, TransactionInCreate, TransactionInDB
from app.infra.transaction.transaction_repository import TransactionRepository
from app.infra.category.category_repository import CategoryRepository
from app.infra.database.models.user import User as UserModel
from app.infra.database.models.category import Category as CategoryModel

class CreateTransactionRequestObject(request_object.ValidRequestObject):
    def __init__(self, transaction_in: TransactionInCreate, current_user: UserModel) -> None:
        self.transaction_in = transaction_in
        self.current_user = current_user

    @classmethod
    def builder(cls, payload: Optional[TransactionInCreate], current_user: UserModel) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return CreateTransactionRequestObject(transaction_in=payload, current_user=current_user)


class CreateTransactionUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository),
                 category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository

    def process_request(self, req_object: CreateTransactionRequestObject):
        transaction_in: TransactionInCreate = req_object.transaction_in
        category: CategoryModel = self.category_repository.get_by_id(req_object.transaction_in.category_id)

        obj_in: TransactionInDB = TransactionInDB(**transaction_in.model_dump(exclude={"category_id"}),
                                                  user=req_object.current_user, category=category)
        transaction_in_db: TransactionInDB = self.transaction_repository.create(transaction=obj_in)
        return Transaction(**transaction_in_db.model_dump())
