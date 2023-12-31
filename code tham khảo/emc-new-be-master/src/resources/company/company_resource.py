import asyncio
from fastapi import UploadFile, File
from typing import Union
from fastapi import APIRouter, Depends
from typing import Annotated

from src.infra.vda.vda_service import vdaService
from src.utils.router import APIRouter
from src.resources.company import company_service
from src.core.user.data import UserCreateUpdate
from src.resources.dependency.dependencies import verify_auth_token, verify_role, unique_token, auth_dependency

router = APIRouter(
    prefix="/company",
    tags=["CompanyDetail"],
)


@router.get("/detail", dependencies=[Depends(auth_dependency)])
async def get_company_detail():
    detail = await vdaService.getCompanyDetail()
    return detail


@router.get("/initialize", dependencies=[Depends(auth_dependency)])
async def initializeFE(user = Depends(auth_dependency)):
    key = company_service.get_initialize_keys()
    company = company_service.get_initialize_company_detail()
    missions = company_service.get_initialize_missions(user)
    Keys, company, missions = await asyncio.gather(key, company, missions)
    return {
        'Keys': Keys,
        'company': company,
        'missions': missions
    }




@router.put("/detail", dependencies=[Depends(auth_dependency)])
async def update_company_detail(data: Union[dict, None] = None, logo: UploadFile = File(...)):
    res = await vdaService.update_company_detail(data, logo)
    return res
