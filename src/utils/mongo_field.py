from typing import Any, Generic, TypeVar

from pydantic import Field
from pydantic.fields import FieldInfo

T = TypeVar("T")


class CompoundIndex:
    def __init__(
        self,
        fields: list[str],
        unique: bool = False,
        sparse: bool = False,
        partial: bool = False,
    ) -> None:
        self.fields = fields
        self.unique = unique
        self.sparse = sparse
        self.partial = partial


class MongoField(Generic[T]):
    def __init__(
        self,
        default: T | None = None,
        *,
        unique: bool = False,
        sparse: bool = False,
        partial: bool = False,
        index: bool = False,
        **kwargs: dict[str, Any],
    ) -> None:
        self.default = default
        self.unique = unique
        self.sparse = sparse
        self.partial = partial
        self.index = index
        self.field_kwargs = kwargs

    def __call__(self) -> FieldInfo:
        extra = {
            "unique": self.unique,
            "sparse": self.sparse,
            "index": self.index,
            "partial": self.partial,
        }
        return Field(
            default=self.default,
            json_schema_extra=extra,
            **self.field_kwargs,
        )
