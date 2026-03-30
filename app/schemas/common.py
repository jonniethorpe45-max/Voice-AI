from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    pagination: Pagination
