"""Configuration settings for Интеграционный сервис Service"""

import sys

sys.path.append("/app/shared")

from core.config.base import (
    IntegrationServiceSettings as BaseIntegrationServiceSettings,
)


class IntegrationServiceSettings(BaseIntegrationServiceSettings):
    """Интеграционный сервис Service specific settings"""

    app_version: str = "1.0.0"
    debug: bool = True
    integration_api_key_secret: str = "CHANGE_ME_SECRET"


settings = IntegrationServiceSettings()
