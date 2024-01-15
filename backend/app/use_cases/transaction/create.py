from typing import Optional
from fastapi import Depends
from app.shared import request_object, use_case

from app.domain.transaction.entity import Transaction, TransactionInCreate, TransactionInDB
from app.infra.transaction.transaction_repository import TransactionRepository
from app.infra.database.models.user import User as UserModel


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
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository)):
        self.transaction_repository = transaction_repository

    def process_request(self, req_object: CreateTransactionRequestObject):
        transaction_in: TransactionInCreate = req_object.transaction_in

        obj_in: TransactionInDB = TransactionInDB(**transaction_in.model_dump(), user=req_object.current_user)
        transaction_in_db: TransactionInDB = self.transaction_repository.create(transaction=obj_in)
        return Transaction(**transaction_in_db.model_dump())
