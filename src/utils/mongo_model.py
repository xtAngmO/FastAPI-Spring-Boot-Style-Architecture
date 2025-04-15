from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, ClassVar, Self, TypeVar
import uuid

from pydantic import BaseModel, Field

T = TypeVar("T", bound="MongoBaseModel")


def collection_name(name: str) -> Callable[[type[T]], type[T]]:
    def decorator(cls: type[T]) -> type[T]:
        cls.collection_name = name
        return cls

    return decorator


class MongoBaseModel(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="created_at", default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(alias="updated_at", default_factory=lambda: datetime.now(UTC))

    collection_name: ClassVar[str] = ""

    model_config: ClassVar[dict[str, bool | dict[type[datetime], Callable[[datetime], str]]]] = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            datetime: lambda dt: dt.isoformat(),
        },
    }

    def dict_for_db(self: Self) -> dict[str, Any]:
        data = self.model_dump(by_alias=True, exclude_unset=False)

        created_at = data.pop("created_at", None)
        data.pop("updated_at", None)

        data["created_at"] = created_at if created_at is not None else datetime.now(UTC)
        data["updated_at"] = datetime.now(UTC)

        return data

    @classmethod
    def from_db(cls: type[Self], data: dict[str, Any]) -> Self:
        if "_id" in data and data["_id"] is not None and not isinstance(data["_id"], str):
            data["_id"] = str(data["_id"])

        for field in ["created_at", "updated_at"]:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)
