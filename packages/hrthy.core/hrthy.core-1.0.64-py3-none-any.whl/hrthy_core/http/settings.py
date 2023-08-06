from functools import lru_cache

from pydantic import BaseSettings


class HttpSettings(BaseSettings):
    alb_url: str = '0.0.0.0',
    cloudfront_secret = ''


@lru_cache()
def get_http_settings() -> HttpSettings:
    return HttpSettings()
