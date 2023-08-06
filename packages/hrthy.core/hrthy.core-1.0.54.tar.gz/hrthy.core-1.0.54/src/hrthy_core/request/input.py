import enum

from pydantic import BaseModel


class SortByRequestInputDto(enum.Enum):
    created_at = 'created_at'
    updated_at = 'updated_at'


class SortDirRequestInputDto(enum.Enum):
    asc = 'asc'
    desc = 'desc'


class OrderedRequestInputDto(BaseModel):
    sort_by: SortByRequestInputDto = SortByRequestInputDto.created_at
    sort_dir: SortDirRequestInputDto = SortDirRequestInputDto.asc


class PaginatedRequestInputDto(BaseModel):
    page: int = 1
    page_size: int = 10

    def get_offset(self) -> int:
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        return self.page_size
