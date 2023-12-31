from src.config.settings import settings
from src.core.user.data import VDAUserRole
from src.infra.secret.secret_service import secret_service
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(
    prefix="/unique-token",
    tags=["UniqueToken"],
)


async def unique_token(req: Request):
    token = req.headers["unique-token"]
    automation_token = await get_automation_token()
    if token != automation_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return {'role': VDAUserRole.Automation}


async def get_automation_token():
    data = secret_service.get_secret(settings.automation_token_secret_name)
    automation_token = data.get('Key')
    return automation_token

