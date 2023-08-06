from enum import Enum

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

from hrthy_core.request.input import SortDirRequestInputDto


def add_pagination(query: Query, page: int, page_size: int) -> Query:
    return query.limit(page_size).offset((page - 1) * page_size)


def add_sorting(query: Query, sort_dir: SortDirRequestInputDto, sort_by: Enum) -> Query:
    sort = asc(sort_by.value) if sort_dir == SortDirRequestInputDto.asc else desc(sort_by.value)
    return query.order_by(sort)
