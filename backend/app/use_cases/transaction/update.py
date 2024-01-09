from typing import Optional
from fastapi import Depends
from app.infra.database.models.category import Category as CategoryModel
from app.shared import request_object, use_case, response_object

from app.domain.transaction.entity import TransactionInUpdate, TransactionInDB, Transaction
from app.infra.transaction.transaction_repository import TransactionRepository


class UpdateTransactionRequestObject(request_object.ValidRequestObject):
    def __init__(self, id: str, obj_in: TransactionInUpdate) -> None:
        self.id = id
        self.obj_in = obj_in

    @classmethod
    def builder(cls, id: str, payload: Optional[TransactionInUpdate]) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if id is None:
            invalid_req.add_error("id", "Invalid transaction id")

        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return UpdateCategoryRequestObject(id=id, obj_in=payload)


class UpdateTransactionUseCase(use_case.UseCase):
    def __init__(self, category_repository: TransactionRepository = Depends(TransactionRepository)):
        self.category_repository = category_repository

    def process_request(self, req_object: UpdateCategoryRequestObject):
        transaction: Optional[CategoryModel] = self.category_repository.get_by_id(req_object.id)
        if not transaction:
            return response_object.ResponseFailure.build_not_found_error("Transaction does not exist")

        self.category_repository.update(id=transaction.id, data=req_object.obj_in)
        transaction.reload()
        return Transaction(**TransactionInDB.model_validate(transaction).model_dump())
