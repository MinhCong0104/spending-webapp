from fastapi import Request, HTTPException, Depends
import boto3
from src.core.user.data import VDAUserRole
from src.resources.user.user_service import user_service
from src.infra.secret.secret_service import secret_service
from src.config.settings import settings

client = boto3.client('cognito-idp')


async def unique_token(req: Request):
    if not req.headers.get('unique-token'):
        return None
    token = req.headers.get('unique-token')
    automation_token = await get_automation_token()
    if token == automation_token:
        return {'role': VDAUserRole.Automation}

async def get_automation_token():
    data = secret_service.get_secret(settings.automation_token_secret_name)
    automation_token = data.get('Key')
    return automation_token




async def verify_auth_token(req: Request):
    if not req.headers.get('Authorization'):
        return None
    token = req.headers.get('Authorization')
    try:
        user_res = client.get_user(AccessToken=token.split(' ')[1])
    except client.exceptions.NotAuthorizedException:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    if user_res is not None:
        vda_user = await user_service.getVDAUserFromUser(user_res)
    else:
        return None
    return dict(vda_user, **user_res)

async def auth_dependency(auth_user = Depends(verify_auth_token),  unique_user = Depends(unique_token)):
    if auth_user:
        return auth_user
    elif unique_user:
        return unique_user
    else:
        raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )

class VerifyRole:
    def __init__(self, require_role):
        self.require_role = require_role

    def __call__(self, auth_user = Depends(auth_dependency)):

        if auth_user['role'] not in self.require_role:
            raise HTTPException(
                status_code=403,
                detail="You don't have the required role",
            )

        return True

verify_role = VerifyRole

