from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.domain.auth.entity import AuthInfoInResponse
from app.shared.decorator import response_decorator
from app.infra.security.security_service import get_current_active_user
from app.use_cases.auth.login import LoginRequestObject, LoginUseCase
from app.use_cases.auth.google import GoogleAuthUseCase, GoogleRequestObject
from app.config import settings

router = APIRouter()


# Set up OAuth
config_data = {"GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID, "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth: OAuth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/login", response_model=AuthInfoInResponse)
@response_decorator()
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_use_case: LoginUseCase = Depends(LoginUseCase),
):
    """Get access token from credentials

    Args:
        form_data (OAuth2PasswordRequestForm, required): contains email, password for login
    Returns:
        access_token: str
    """
    login_request_object = LoginRequestObject.builder(
        data=dict(email=form_data.username, password=form_data.password),
    )
    response = login_use_case.execute(request_object=login_request_object)
    return response


@router.get("/google/authorize")
async def google_authorize(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


@router.get("/google/token", response_model=AuthInfoInResponse)
@response_decorator()
def google_token(id_token: str, google_auth_use_case: GoogleAuthUseCase = Depends(GoogleAuthUseCase)):
    google_request_object = GoogleRequestObject.builder(id_token=id_token)
    response = google_auth_use_case.process_request(google_request_object)
    return response


@router.post("/logout", dependencies=[Depends(get_current_active_user)])
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return True
