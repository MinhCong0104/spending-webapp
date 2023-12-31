from fastapi import Request, HTTPException, Depends, Form, UploadFile, Body
from src.utils.router import APIRouter
from src.config.settings import settings
from src.infra.vda.vda_service import vdaService
import boto3
from src.core.user.data import ListQueryOptions, UserCreateUpdate, UserGroup, VDAUserRole, TemporaryPassword
from typing import List, Optional, Annotated
from pydantic import BaseModel, NonNegativeFloat
from src.resources.dependency.dependencies import auth_dependency, verify_auth_token, verify_role
from src.resources.user.user_service import user_service
from dataclasses import asdict
from src.utils.error.error import AppException
import json

router = APIRouter(
    prefix="/users",
    tags=["User"],
)

client = boto3.client('cognito-idp')


@router.get('/auth-events', dependencies=[Depends(auth_dependency)])
async def get_user_auth_events(query: ListQueryOptions = Depends()):
    response = await user_service.list_user_auth_events(query)
    return response

@router.get('/currentUser', dependencies=[Depends(auth_dependency)])
async def current_user(auth_user: dict =  Depends(verify_auth_token)):
    return auth_user

@router.post('', dependencies=[Depends(verify_role([VDAUserRole.Admin,VDAUserRole.SuperAdmin]))])
async def create_user(data: UserCreateUpdate = Depends(), avatar: Optional[UploadFile] = None):
    dict_data = asdict(data)
    load_json_field(dict_data, ['assign', 'company'])
    vda_user = await user_service.create_new_user(data, avatar)
    return vda_user

@router.post('/new', dependencies=[Depends(verify_role([VDAUserRole.Admin,VDAUserRole.SuperAdmin]))])
async def create_user(data: UserCreateUpdate = Depends(), avatar: Optional[UploadFile] = None):
    dict_data = asdict(data)
    load_json_field(dict_data, ['assign', 'company'])
    vda_user = await user_service.create_new_user(dict_data, avatar)
    return vda_user

@router.put('/{id}', dependencies=[Depends(auth_dependency)])
async def update_user(id: str, data: UserCreateUpdate = Depends(), avatar: Optional[UploadFile] = None):
    dict_data = asdict(data)
    load_json_field(dict_data, ['assign', 'company'])
    user = await user_service.update_user(id, dict_data, avatar)
    return user

def load_json_field(data: dict, fields: list[str]):
    for f in fields:
        if data.get(f):
            data[f] = json.loads(data.get(f))

@router.get('/{id}', dependencies=[Depends(auth_dependency)])
async def get_user_detail(id: str):
    user = await user_service.get_user_by_id(id)
    return user

@router.delete('/{id}', dependencies=[Depends(verify_role([VDAUserRole.Admin,VDAUserRole.SuperAdmin]))])
async def delete_user(id: str):
    user = await user_service.delete_user(id)
    return user

@router.post('/{id}/resetTemporaryPassword', dependencies=[Depends(verify_role([VDAUserRole.Admin,VDAUserRole.SuperAdmin]))])
async def reset_temporary_password(id: str, data: TemporaryPassword = Body(...)):
    user = await vdaService.getUserDetail(id)
    if not user.get('_id'):
        raise AppException(name='User not found')
    await user_service.reset_temporary_password(user, data.temporary_password)


