from typing import Optional
from fastapi import Depends
from app.shared import request_object, use_case

from app.domain.transaction.entity import Transaction, TransactionInCreate, TransactionInDB
from app.infra.transaction.transaction_repository import TransactionRepository


class CreateTransactionRequestObject(request_object.ValidRequestObject):
    def __init__(self, transaction_in: TransactionInCreate = None) -> None:
        self.transaction_in = transaction_in

    @classmethod
    def builder(cls, payload: Optional[TransactionInCreate] = None) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if payload is None:
            invalid_req.add_error("payload", "Invalid payload")

        if invalid_req.has_errors():
            return invalid_req

        return CreateTransactionRequestObject(transaction_in=payload)


class CreateTransactionUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository)):
        self.transaction_repository = transaction_repository

    def process_request(self, req_object: CreateTransactionRequestObject):
        transaction_in: TransactionInCreate = req_object.transaction_in

        obj_in: TransactionInDB = TransactionInDB(**user_in.model_dump())
        transaction_in_db: TransactionInDB = self.transaction_repository.create(transaction=obj_in)
        return Transaction(**transaction_in_db.model_dump())
