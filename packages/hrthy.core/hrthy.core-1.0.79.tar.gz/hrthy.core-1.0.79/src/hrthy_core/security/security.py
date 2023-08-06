from enum import Enum
from time import time
from typing import List
from uuid import UUID

from fastapi import Depends
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from jose import jwt
from pydantic.main import BaseModel

from hrthy_core.request.exceptions import UnauthorizedHTTPException, NotEnoughPermissionsHTTPException
from hrthy_core.security.scopes import SCOPE_REFRESH_TOKEN
from hrthy_core.security.settings import SecuritySettings, get_security_settings


class RequesterType(Enum):
    user = 'user'
    service = 'service'


class Token(BaseModel):
    access_token: str
    token_type: str


class Requester(BaseModel):
    requester_type: RequesterType
    requester_id: UUID
    company_id: UUID = None
    role_id: UUID = None
    scopes: List[str] = []


AUTH_ISS = 'hrthy.com'


async def get_jwt_payload(
        settings: SecuritySettings = Depends(get_security_settings),
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))
) -> dict:
    try:
        return jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_algorithm])
    except Exception:
        raise UnauthorizedHTTPException()


async def get_requester(
        security_scopes: SecurityScopes,
        jwt_payload: dict = Depends(get_jwt_payload)
):
    try:
        requester_id: UUID = UUID(jwt_payload.get('sub'), version=4)
        company_id: str = jwt_payload.get('company_id', None)
        role_id: str = jwt_payload.get('role_id', None)
        requester_type: str = jwt_payload.get('type')
        token_scopes = jwt_payload.get("scopes", [])
        requester = Requester(
            requester_type=RequesterType[requester_type],
            requester_id=requester_id,
            company_id=None if company_id is None else UUID(company_id, version=4),
            role_id=None if role_id is None else UUID(role_id, version=4),
            scopes=token_scopes
        )
    except Exception:
        raise UnauthorizedHTTPException()
    # If no scope are required, return the requester
    if not security_scopes.scopes:
        return requester
    # Otherwise check if the requester has at least one scope
    for scope in security_scopes.scopes:
        if scope in requester.scopes:
            return requester
    # Requester doesn't have any requested scope
    raise NotEnoughPermissionsHTTPException()


def generate_jwt_token(
        sub: UUID,
        requester_type: RequesterType,
        scopes: list,
        company_id: UUID = None,
        role_id: UUID = None,
) -> str:
    settings: SecuritySettings = get_security_settings()
    data = {
        'iss': AUTH_ISS,
        'sub': str(sub),
        'type': requester_type.value,
        'iat': int(time()),
        'exp': int(time() + settings.auth_token_ttl),
        'scopes': scopes
    }
    if company_id is not None:
        data.update({'company_id': str(company_id)})
    if role_id is not None:
        data.update({'role_id': str(role_id)})
    return jwt.encode(data, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def generate_jwt_refresh_token(
        sub: UUID,
        requester_type: RequesterType,
        company_id: UUID = None,
        role_id: UUID = None
) -> str:
    settings: SecuritySettings = get_security_settings()
    data = {
        'iss': AUTH_ISS,
        'sub': str(sub),
        'type': requester_type.value,
        'iat': int(time()),
        'exp': int(time() + settings.auth_refresh_token_ttl),
        'scopes': [SCOPE_REFRESH_TOKEN]
    }
    if company_id is not None:
        data.update({'company_id': str(company_id)})
    if role_id is not None:
        data.update({'role_id': str(role_id)})
    return jwt.encode(data, settings.auth_secret_key, algorithm=settings.auth_algorithm)
