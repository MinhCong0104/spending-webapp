from fastapi import APIRouter, Body, Depends, Path, Query
from typing import Annotated, Union
from app.domain.transaction.entity import Transaction, TransactionInCreate, TransactionInDB, TransactionInUpdate
from app.infra.security.security_service import get_current_active_user, get_current_administrator
from app.shared.decorator import response_decorator
from app.domain.shared.enum import UserRole, Type
from app.infra.database.models.user import User as UserModel
from app.infra.database.models.category import Category as CategoryModel

from app.use_cases.transaction.get import GetTransactionRequestObject, GetTransactionUseCase
from app.use_cases.transaction.create import CreateTransactionRequestObject, CreateTransactionUseCase
from app.use_cases.transaction.list import ListTransactionsRequestObject, ListTransactionsUseCase
from app.use_cases.transaction.update import UpdateTransactionRequestObject, UpdateTransactionUseCase

router = APIRouter()


@router.get(
    "/{transaction_id}",
    dependencies=[Depends(get_current_active_user)],  # auth route
    response_model=Transaction,
)
@response_decorator()
def get_transaction(
    transaction_id: str = Path(..., title="Category id"),
    get_transaction_use_case: GetTransactionUseCase = Depends(GetTransactionUseCase),
):
    req_object = GetTransactionRequestObject.builder(transaction_id=transaction_id)
    response = get_transaction_use_case.execute(request_object=req_object)
    return response


@router.post(
    "",
    dependencies=[Depends(get_current_active_user)],
    response_model=Transaction,
)
@response_decorator()
def create_transaction(
    payload: TransactionInCreate = Body(..., title="TransactionInCreate payload"),
    current_user: UserModel = Depends(get_current_active_user),
    create_transaction_use_case: CreateTransactionUseCase = Depends(CreateTransactionUseCase),
):
    req_object = CreateTransactionRequestObject.builder(payload=payload, current_user=current_user)
    response = create_transaction_use_case.execute(request_object=req_object)
    return response


@router.get("")
@response_decorator()
def get_list_transaction(
    current_user: UserModel = Depends(get_current_active_user),
    list_transactions_use_case: ListTransactionsUseCase = Depends(ListTransactionsUseCase),
    type: Annotated[Union[Type, None], Query(title="Transaction Type")] = None,
    category: Annotated[str, Query(title="Category Id")] = None,
    date_from: Annotated[Union[str, None], Query(title="From Date")] = None,
    date_to: Annotated[Union[str, None], Query(title="To Date")] = None,
):
    req_object = ListTransactionsRequestObject.builder(current_user=current_user, type=type, category=category,
                                                       date_from=date_from, date_to=date_to)
    response = list_transactions_use_case.execute(request_object=req_object)
    return response


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_administrator)],  # auth route
    response_model=Transaction,
)
@response_decorator()
def update_transaction(
    id: str = Path(..., title="Transaction Id"),
    payload: TransactionInUpdate = Body(..., title="Transaction updated payload"),
    update_transaction_use_case: UpdateTransactionUseCase = Depends(UpdateTransactionUseCase),
):
    req_object = UpdateTransactionRequestObject.builder(id=id, payload=payload)
    response = update_transaction_use_case.execute(request_object=req_object)
    return response
