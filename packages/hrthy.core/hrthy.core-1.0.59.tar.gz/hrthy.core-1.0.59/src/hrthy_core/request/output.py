from typing import List

from pydantic import typing
from pydantic.main import BaseModel


class BaseItemOutputDto(BaseModel):
    item: typing.Any = None


class BaseListItemOutputDto(BaseModel):
    items: List[BaseItemOutputDto] = []
    total_count: int = 0
