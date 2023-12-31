from pydantic import ValidationError
from starlette.exceptions import HTTPException

from src.resources.health_check import health_check_resource
from src.resources.roof_score import roof_score_resource
from src.resources.user import user_resource, user_tasks_service
from src.resources.company import company_resource
from src.resources.missions import mission_resource
from src.resources.roof_score import score_resource
from src.infra.database import connect_db, close_db
from src.utils.error.error import AppException

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# from fastapi_contrib.common.middlewares import StateRequestIDMiddleware
# from fastapi_contrib.tracing.middlewares import OpentracingMiddleware

# from app.utils.config import TRACER_IS_ENABLED
# from app.utils.tracer_config import tracer
# from app.utils.exception.exception_handlers import ExceptionHandlers
# from app.utils.pydiator.pydiator_core_config import set_up_pydiator
# from app.utils.exception.exception_types import DataException, ServiceException


def create_app():
    app = FastAPI(
        title="EMC webserver",
        description="FastAPI EMC webserver",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/doc",
        redoc_url="/redoc"
    )

    origins = [
        "*", # TODO: specify correct origin later
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_exception_handler(Exception, ExceptionHandlers.unhandled_exception)
    # app.add_exception_handler(DataException, ExceptionHandlers.data_exception)
    # app.add_exception_handler(ServiceException, ExceptionHandlers.service_exception)
    # app.add_exception_handler(HTTPException, ExceptionHandlers.http_exception)
    # app.add_exception_handler(ValidationError, ExceptionHandlers.validation_exception)

    app.include_router(
        health_check_resource.router,
    )

    app.include_router(
        roof_score_resource.router,
    )

    app.include_router(
        user_resource.router,
    )

    app.include_router(
        user_tasks_service.router,
    )

    app.include_router(
        company_resource.router,
    )

    app.include_router(
        mission_resource.router,
    )

    app.include_router(
        score_resource.router,
    )

    @app.on_event('startup')
    async def startup():
        connect_db()

    @app.on_event('shutdown')
    async def shutdown():
        close_db()

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=200,
            content={"error": exc.name},
        )

    return app
