import math
from typing import Optional, List
from fastapi import Depends
from app.shared import request_object, use_case
from app.domain.user.entity import User
from app.domain.category.entity import Category
from app.domain.transaction.entity import Transaction, TransactionInDB
from app.infra.database.models.transaction import Transaction as TransactionModel
from app.infra.transaction.transaction_repository import TransactionRepository
from app.infra.category.category_repository import CategoryRepository
from app.domain.shared.enum import Type


class ListTransactionsRequestObject(request_object.ValidRequestObject):
    def __init__(
        self,
        current_user: User,
        date_from: str,
        date_to: str,
        type: Type,
        category_id: str,
        note: str

    ):
        self.current_user = current_user
        self.date_from = date_from
        self.date_to = date_to
        self.type = type
        self.category_id = category_id
        self.note = note

    @classmethod
    def builder(
        cls,
        current_user: User,
        type: Optional[Type] = None,
        note: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> request_object.RequestObject:
        return ListTransactionsRequestObject(current_user=current_user, type=type, category_id=category_id,
                                             date_from=date_from, date_to=date_to, note=note)


class ListTransactionsUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository),
                 category_repository: CategoryRepository = Depends(CategoryRepository)):
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository

    def process_request(self, req_object: ListTransactionsRequestObject):
        if req_object.category_id:
            category: Category = self.category_repository.get_by_id(req_object.category_id)

        transactions: List[TransactionModel] = self.transaction_repository.list(
            user=req_object.current_user.id,
            type=req_object.type,
            category=category.id if req_object.category_id else None,
            date_from=req_object.date_from,
            date_to=req_object.date_to,
            note=req_object.note
        )

        data = [Transaction(**TransactionInDB.model_validate(model).model_dump()) for model in transactions]
        return data
