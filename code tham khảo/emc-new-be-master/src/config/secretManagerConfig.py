from typing import Any
from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable

from src.infra.secret.secret_service import secret_service


class SecretManagerConfig:
    @classmethod
    def get_secrets(cls, settings: BaseSettings) -> dict[str, Any]:
        # We go through the fields and try to fetch a secret with that field name
        return {
            name: secret_service.get_secret(name) for name, _ in settings.__fields__.items()
        }

    @classmethod
    def customise_sources(
        cls,
        init_settings: SettingsSourceCallable,
        env_settings: SettingsSourceCallable,
        file_secret_settings: SettingsSourceCallable,
    ):
        # Here we add the `cls.get_secrets` method as an extra data source
        return (
            init_settings,
            cls.get_secrets,
            env_settings,
            file_secret_settings,
        )