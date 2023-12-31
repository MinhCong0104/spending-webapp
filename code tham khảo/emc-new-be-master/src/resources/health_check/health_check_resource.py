
   
from fastapi import status
from fastapi.responses import PlainTextResponse
from src.utils.router import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health check"],
)


@router.get("",
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_200_OK: {
                    "model": str,
                    "content": {
                        "text/plain": {
                            "example": "OK"
                        }
                    }
                }
            },
            response_class=PlainTextResponse)
async def get():
    return "OK"