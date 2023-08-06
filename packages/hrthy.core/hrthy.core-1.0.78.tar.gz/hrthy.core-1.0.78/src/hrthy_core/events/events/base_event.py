from time import time
from uuid import UUID

from pydantic import typing, Field
from pydantic.main import BaseModel

from hrthy_core.security.security import Requester


class BaseEvent(BaseModel):
    type: str = 'BaseEvent'
    timestamp: int = Field(default_factory=lambda: int(time()))
    requester: Requester
    payload: typing.Any


class BasePayload(BaseModel):
    id: UUID


class CompanyBasePayload(BasePayload):
    company_id: UUID
