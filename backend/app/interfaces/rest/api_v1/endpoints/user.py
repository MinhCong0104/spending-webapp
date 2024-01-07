from fastapi import APIRouter, Body, Depends, Path, Query
from typing import Annotated, Union
from app.domain.user.entity import User, UserInCreate, UserInDB, ManyUsersInResponse, UserInUpdate
from app.infra.security.security_service import get_current_active_user, get_current_administrator
from app.shared.decorator import response_decorator
from app.infra.database.models.user import User as UserModel
from app.use_cases.user.list import ListUsersUseCase, ListUsersRequestObject
from app.use_cases.user.update import UpdateUserUseCase, UpdateUserRequestObject
from app.domain.shared.enum import UserRole

from app.use_cases.user.get import (
    GetUserRequestObject,
    GetUserCase,
)
from app.use_cases.user.create import (
    CreateUserRequestObject,
    CreateUserUseCase,
)

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    get current user data
    :param current_user:
    :return:
    """
    return User(**UserInDB.model_validate(current_user).model_dump())


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_active_user)],  # auth route
    response_model=User,
)
@response_decorator()
def get_user(
    user_id: str = Path(..., title="User id"),
    get_user_use_case: GetUserCase = Depends(GetUserCase),
):
    get_user_request_object = GetUserRequestObject.builder(user_id=user_id)
    response = get_user_use_case.execute(request_object=get_user_request_object)
    return response


@router.post(
    "",
    dependencies=[Depends(get_current_active_user)],
    response_model=User,
)
@response_decorator()
def create_user(
    payload: UserInCreate = Body(..., title="UserInCreate payload"),
    create_user_use_case: CreateUserUseCase = Depends(CreateUserUseCase),
):
    req_object = CreateUserRequestObject.builder(payload=payload)
    response = create_user_use_case.execute(request_object=req_object)
    return response


@router.get("", response_model=ManyUsersInResponse)
@response_decorator()
def get_list_users(
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
