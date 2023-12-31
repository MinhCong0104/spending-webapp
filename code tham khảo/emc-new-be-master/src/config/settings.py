from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    port: int

    db_host: Optional[str] = None
    connect_db_port: Optional[int] = None
    db_name: Optional[str] = None
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None

    db_credential_secret_name: Optional[str] = None

    report_s3: str = ''
    aws_default_region: str = ''

    vda_api_secret_name: str = ''

    automation_token_secret_name: str = ''
    vda_id_attribute: str = ''

    google_maps_secret_name: str = ''
    user_pool_id: str = ''
    mail_secret_name: str = ''
    support_email: str = ''
    emc_owned_resources_secret_name: str = ''

    temporary_password: str = ''
    http_client_time_out: int = 30000
    fe_host: str = ''
    class Config:
        secrets_dir = '/run/secrets'  # https://pydantic-docs.helpmanual.io/usage/settings/#use-case-docker-secrets


settings = Settings()
