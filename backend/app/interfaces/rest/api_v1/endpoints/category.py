from fastapi import APIRouter, Body, Depends, Path, Query
from typing import Annotated, Union
from app.domain.category.entity import Category, CategoryInCreate, CategoryInDB, CategoryInUpdate
from app.infra.security.security_service import get_current_active_user, get_current_administrator
from app.shared.decorator import response_decorator
from app.infra.database.models.user import User as UserModel
from app.domain.shared.enum import UserRole

from app.use_cases.category.get import GetCategoryRequestObject, GetCategoryUseCase
from app.use_cases.category.create import CreateCategoryUseCase, CreateCategoryRequestObject
from app.use_cases.user.list import ListUsersUseCase, ListUsersRequestObject
from app.use_cases.user.update import UpdateUserUseCase, UpdateUserRequestObject

router = APIRouter()


@router.get(
    "/{category_id}",
    dependencies=[Depends(get_current_active_user)],  # auth route
    response_model=Category,
)
@response_decorator()
def get_category(
    category_id: str = Path(..., title="Category id"),
    get_category_use_case: GetCategoryUseCase = Depends(GetCategoryUseCase),
):
    get_category_request_object = GetCategoryRequestObject.builder(category_id=category_id)
    response = get_category_use_case.execute(request_object=get_category_request_object)
    return response


@router.post(
    "",
    dependencies=[Depends(get_current_active_user)],
    response_model=Category,
)
@response_decorator()
def create_category(
    payload: CategoryInCreate = Body(..., title="CategoryInCreate payload"),
    create_category_use_case: CreateCategoryUseCase = Depends(CreateCategoryUseCase),
):
    req_object = CreateCategoryRequestObject.builder(payload=payload)
    response = create_category_use_case.execute(request_object=req_object)
    return response


@router.get("")
@response_decorator()
def get_list_categories(
    current_user: UserModel = Depends(get_current_administrator),
    list_users_use_case: ListUsersUseCase = Depends(ListUsersUseCase),
    page_index: Annotated[int, Query(title="Page Index")] = 1,
    page_size: Annotated[int, Query(title="Page size")] = 100,
    role: Annotated[UserRole, Query(title="User role")] = UserRole.USER,
    email: Annotated[Union[str, None], Query(title="Email")] = None,
):
    req_object = ListUsersRequestObject.builder(
        current_user=current_user, page_size=page_size, page_index=page_index, role=role, email=email
    )
    response = list_users_use_case.execute(request_object=req_object)
    return response


@router.get(
    "/admin/{id}",
    dependencies=[Depends(get_current_administrator)],  # auth route
    response_model=User,
)
@response_decorator()
def admin_get_user(
    id: str = Path(..., title="User id"),
    get_user_use_case: GetUserCase = Depends(GetUserCase),
):
    req_object = GetUserRequestObject.builder(user_id=id)
    response = get_user_use_case.execute(request_object=req_object)
    return response


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_administrator)],  # auth route
    response_model=User,
)
@response_decorator()
def update_user(
    id: str = Path(..., title="User Id"),
    payload: UserInUpdate = Body(..., title="User updated payload"),
    update_user_use_case: UpdateUserUseCase = Depends(UpdateUserUseCase),
):
    req_object = UpdateUserRequestObject.builder(id=id, payload=payload)
    response = update_user_use_case.execute(request_object=req_object)
    return response
