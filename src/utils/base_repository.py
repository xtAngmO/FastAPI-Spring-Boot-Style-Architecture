from datetime import UTC, datetime
from typing import Generic, Self, TypeVar

from src.configs.database_config import MongoDB
from src.utils.data_pagination import PaginatedResponse, paginate
from src.utils.mongo_model import MongoBaseModel

T = TypeVar("T", bound=MongoBaseModel)


class BaseRepository(Generic[T]):
    def __init__(self: Self, entity_class: type[T]) -> None:
        self.entity_class = entity_class
        self.collection = MongoDB().get_collection(entity_class.collection_name)

    async def find_all(self: Self, skip: int = 0, limit: int = 100) -> PaginatedResponse:
        return await paginate(self.collection, {}, skip, limit)

    async def find_by_id(self: Self, id: str) -> T | None:
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.entity_class(**doc)
        return None

    async def find_by_filter(self: Self, filter_query: dict) -> list[T]:
        cursor = self.collection.find(filter_query)
        result = []
        async for doc in cursor:
            result.append(self.entity_class(**doc))
        return result

    async def find_one_by_filter(self: Self, filter_query: dict) -> T | None:
        doc = await self.collection.find_one(filter_query)
        if doc:
            return self.entity_class(**doc)
        return None

    async def create(self: Self, entity: T) -> T:
        entity_dict = entity.dict_for_db()
        result = await self.collection.insert_one(entity_dict)
        entity.id = result.inserted_id
        return entity

    async def update(self: Self, id: str, entity: T) -> T | None:
        entity_dict = entity.dict_for_db()
        entity_dict["updated_at"] = datetime.now(tz=UTC)

        await self.collection.update_one(
            {"_id": id},
            {"$set": entity_dict},
        )
        return await self.find_by_id(id)

    async def delete(self: Self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
