from datetime import datetime
from math import ceil
from typing import Any, ClassVar, Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel

T = TypeVar("T")

MongoValue = str | int | float | bool | datetime | dict[str, Any] | list[Any]
MongoDocument = dict[str, MongoValue]


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    page: int
    limit: int
    total: int
    total_pages: int

    model_config: ClassVar[dict[str, bool]] = {
        "arbitrary_types_allowed": True,
    }


async def paginate(
    collection: AsyncIOMotorCollection,
    filter_query: dict[str, MongoValue],
    skip: int = 0,
    limit: int = 100,
) -> PaginatedResponse[MongoDocument]:
    total: int = await collection.count_documents(filter_query)
    cursor: AsyncIOMotorCursor = collection.find(filter_query).skip(skip).limit(limit)

    data: list[MongoDocument] = []
    async for document in cursor:
        if "_id" in document:
            document["_id"] = str(document["_id"])
        data.append(document)

    page: int = skip // limit + 1 if limit > 0 else 1
    total_pages: int = ceil(total / limit) if limit > 0 else 1

    return PaginatedResponse(
        data=data,
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
    )
