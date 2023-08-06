from pydantic.env_settings import BaseSettings
from pydantic.error_wrappers import ValidationError


class HumanloopSettings(BaseSettings):
    api_key: str
    api_base_url: str

    class Config:
        env_prefix = "HUMANLOOP_"


def get_humanloop_settings(**overrides):
    """Get settings for the Humanloop API client

    Used to read environment variables.
    """
    try:
        _settings = HumanloopSettings(**overrides)
    except ValidationError:
        raise ValueError(
            "Humanloop client settings is not configured. "
            "Configure it with environment variables or `hl.init()`."
        )
    return _settings
