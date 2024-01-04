from fastapi import Depends
from typing import Optional
from app.shared import request_object, response_object, use_case
from app.domain.transaction.entity import Transaction, TransactionInDB
from app.infra.transaction.transaction_repository import TransactionRepository
from app.infra.database.models.transaction import Transaction as TransactionModel


class GetTransactionRequestObject(request_object.ValidRequestObject):
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    @classmethod
    def builder(cls, transaction_id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return GetTransactionRequestObject(transaction_id=transaction_id)


class GetCategoryUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository)):
        self.transaction_repository = transaction_repository

    def process_request(self, req_object: GetTransactionRequestObject):
        transaction: Optional[TransactionModel] = self.transaction_repository.get_by_id(id=req_object.transaction_id)
        if not transaction:
            return response_object.ResponseFailure.build_not_found_error(message="Transaction does not exist.")

        return Transaction(**TransactionInDB.model_validate(transaction).model_dump())
