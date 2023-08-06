from functools import lru_cache

from pydantic import BaseSettings


class SecuritySettings(BaseSettings):
    auth_secret_key: str = 'dbcd5de4e9348fca4264011b218cf14e9c87656da575864c7017a0b745c41f0d'
    auth_algorithm: str = 'HS256'
    auth_token_ttl: int = 300  # 5 minutes
    auth_refresh_token_ttl: int = 2592000  # 30 days


@lru_cache()
def get_security_settings() -> SecuritySettings:
    return SecuritySettings()
