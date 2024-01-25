from typing import Optional
from fastapi import Depends
from app.shared import request_object, response_object, use_case
from app.infra.database.models.transaction import Transaction as TransactionModel
from app.infra.transaction.transaction_repository import TransactionRepository


class DeleteTransactionRequestObject(request_object.ValidRequestObject):
    def __init__(self, id: str):
        self.id = id

    @classmethod
    def builder(cls, id: str) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not id:
            invalid_req.add_error("id", "Invalid")

        if invalid_req.has_errors():
            return invalid_req

        return DeleteTransactionRequestObject(id=id)


class DeleteTransactionUseCase(use_case.UseCase):
    def __init__(self, transaction_repository: TransactionRepository = Depends(TransactionRepository)):
        self.transaction_repository = transaction_repository

    def process_request(self, req_object: DeleteTransactionRequestObject):
        transaction: Optional[TransactionModel] = self.transaction_repository.get_by_id(id=req_object.id)
        if not transaction:
            return response_object.ResponseFailure.build_not_found_error(message="Transaction does not exist.")
        self.transaction_repository.delete(req_object.id)
        return {"success": True}
