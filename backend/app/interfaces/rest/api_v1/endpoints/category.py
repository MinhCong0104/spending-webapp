from fastapi import APIRouter, Body, Depends, Path, Query
from typing import Annotated, Union
from app.domain.category.entity import Category, CategoryInCreate, CategoryInDB, CategoryInUpdate
from app.infra.security.security_service import get_current_active_user, get_current_administrator
from app.shared.decorator import response_decorator
from app.domain.shared.enum import UserRole, Type

from app.use_cases.category.get import GetCategoryRequestObject, GetCategoryUseCase
from app.use_cases.category.create import CreateCategoryUseCase, CreateCategoryRequestObject
from app.use_cases.category.list import ListCategoriesUseCase, ListCategoriesRequestObject
from app.use_cases.category.update import UpdateCategoryUseCase, UpdateCategoryRequestObject

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
    req_object = GetCategoryRequestObject.builder(category_id=category_id)
    response = get_category_use_case.execute(request_object=req_object)
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
    current_user: UserModel = Depends(get_current_active_user),
    list_categories_use_case: ListCategoriesUseCase = Depends(ListCategoriesUseCase),
    type: Annotated[Union[Type, None], Query(title="Category Type")] = None,
    name: Annotated[Union[Type, None], Query(title="Category Name")] = None,
    note: Annotated[Union[str, None], Query(title="Category Note")] = None,
):
    req_object = ListCategoriesRequestObject.builder(current_user=current_user, type=type,
                                                     name=name, note=note)
    response = list_categories_use_case.execute(request_object=req_object)
    return response


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_administrator)],  # auth route
    response_model=Category,
)
@response_decorator()
def update_category(
    id: str = Path(..., title="Category Id"),
    payload: CategoryInUpdate = Body(..., title="Category updated payload"),
    update_category_use_case: UpdateCategoryUseCase = Depends(UpdateCategoryUseCase),
):
    req_object = UpdateCategoryRequestObject.builder(id=id, payload=payload)
    response = update_category_use_case.execute(request_object=req_object)
    return response
