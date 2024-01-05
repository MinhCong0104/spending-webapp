import math
from typing import Optional, List
from fastapi import Depends
from app.shared import request_object, use_case
from app.domain.user.entity import User
from app.domain.transaction.entity import Transaction, TransactionInDB
from app.infra.database.models.transaction import Transaction as TransactionModel
from app.infra.transaction.transaction_repository import TransactionRepository
from app.domain.shared.enum import Type


class ListTransactionsRequestObject(request_object.ValidRequestObject):
    def __init__(
        self,
        current_user: User,
        date_from: str,
        date_to: str,
        type: Type,
        category: str,

    ):
        self.current_user = current_user
        self.date_from = date_from
        self.date_to = date_to
        self.type = type
        self.category = category

    @classmethod
    def builder(
        cls,
        current_user: User,
        type: Optional[Type] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        category: Optional[str] = None,
    ) -> request_object.RequestObject:
        return ListTransactionsRequestObject(current_user=current_user, type=type, category=category,
                                             date_from=date_from, date_to=date_to)


class ListTransactionsUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: Transaction = Depends(TransactionRepository)):
        self.transaction_repository = transaction_repository

    def process_request(self, req_object: ListTransactionsRequestObject):

        transactions: List[TransactionModel] = self.transaction_repository.list(
            user=req_object.current_user,
            type=req_object.type,
            category=req_object.category,
            date_from=req_object.date_from,
            date_to=req_object.date_to,
        )

        data = [Transaction(**TransactionInDB.model_validate(model).model_dump()) for model in transactions]
        return data
