from enum import Enum
import inspect
import sys
from typing import Any, Self, Union, cast, get_args, get_origin

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from src.configs.logging_config import logger
from src.utils.mongo_model import MongoBaseModel

IndexField = tuple[str, int]
IndexFields = list[IndexField]


class MongoSetup:
    @classmethod
    def _get_field_type(cls, annotation: type | None, args: tuple[Any, ...]) -> str:
        field_type: str = "string"
        if annotation:
            types = [arg for arg in args if arg is not type(None)]
            if types and types[0] is str:
                field_type = "string"
            elif types and types[0] is int:
                field_type = "number"
            elif types and types[0] in (bool, Enum):
                field_type = "bool"
        return field_type

    @classmethod
    async def _create_index_with_options(
        cls,
        collection: AsyncIOMotorCollection,
        index_fields: IndexFields,
        is_unique: bool = False,
        is_sparse: bool = False,
        partial: bool = False,
        field_type: str = "string",
        index_name: str | None = None,
    ) -> None:
        index_options: dict[str, Any] = {
            "unique": is_unique,
            "sparse": is_sparse,
        }

        if index_name:
            index_options["name"] = index_name

        if partial:
            field_name: str = index_fields[0][0] if isinstance(index_fields[0], tuple) else index_fields[0]
            index_options["partialFilterExpression"] = {
                field_name: {"$exists": True, "$type": field_type},
            }

        await collection.create_index(index_fields, **index_options)

    @classmethod
    async def _ensure_collections_exist(cls: type[Self], database: AsyncIOMotorDatabase) -> None:
        logger.info("Ensuring MongoDB collections exist...")
        models: list[type[MongoBaseModel]] = []

        for module_name, module in sys.modules.items():
            if module_name.startswith("src.entities"):
                for _, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, MongoBaseModel)
                        and obj != MongoBaseModel
                        and hasattr(obj, "collection_name")
                        and obj.collection_name
                    ):
                        models.append(cast(type[MongoBaseModel], obj))

        existing_collections: list[str] = await database.list_collection_names()

        for model in models:
            if model.collection_name not in existing_collections:
                logger.info(f"Creating collection: {model.collection_name}")
                await database.create_collection(model.collection_name)

            collection: AsyncIOMotorCollection = database[model.collection_name]

            existing_indexes = await collection.list_indexes().to_list(None)
            existing_index_names: list[str] = [idx.get("name") for idx in existing_indexes]

            for base_field in ["created_at"]:
                index_name: str = f"{base_field}_1"
                if index_name not in existing_index_names:
                    await collection.create_index(base_field)

            model_fields: dict[str, Any] = model.model_fields if hasattr(model, "model_fields") else {}

            for field_name, field_info in model_fields.items():
                field_extras: dict[str, Any] = getattr(field_info, "json_schema_extra", {}) or {}

                if not isinstance(field_extras, dict) or not any(field_extras.get(key, False) for key in ["unique", "index"]):
                    continue

                index_name: str = f"{field_name}_1"
                is_unique: bool = field_extras.get("unique", False)
                is_sparse: bool = field_extras.get("sparse", False)
                is_partial: bool = field_extras.get("partial", False)
                needs_index: bool = field_extras.get("index", False) or is_unique

                if not needs_index:
                    continue

                is_optional: bool = False
                try:
                    annotation: Any = getattr(field_info, "annotation", None)
                    origin: Any = get_origin(annotation)
                    args: tuple[Any, ...] = get_args(annotation)

                    if origin is Union and type(None) in args:
                        is_optional = True
                except (AttributeError, TypeError):
                    pass

                if index_name in existing_index_names and (is_unique and (is_optional or is_sparse or is_partial)):
                    await collection.drop_index(index_name)
                    existing_index_names.remove(index_name)

                if is_unique and (is_optional or is_sparse or is_partial):
                    field_type: str = cls._get_field_type(annotation, args)

                    await cls._create_index_with_options(
                        collection=collection,
                        index_fields=[(field_name, 1)],
                        is_unique=True,
                        is_sparse=is_sparse,
                        partial=True,
                        field_type=field_type,
                        index_name=index_name,
                    )

                elif needs_index and index_name not in existing_index_names:
                    await cls._create_index_with_options(
                        collection=collection,
                        index_fields=[(field_name, 1)],
                        is_unique=is_unique,
                        is_sparse=is_sparse,
                        partial=is_partial,
                        index_name=index_name,
                    )

            if hasattr(model, "compound_indexes") and model.compound_indexes:
                for compound_idx in model.compound_indexes:
                    index_fields: IndexFields = [(field, 1) for field in compound_idx.fields]
                    index_name: str = "_".join([f"{field}_1" for field in compound_idx.fields])

                    if index_name in existing_index_names:
                        continue

                    logger.info(f"Creating compound index {index_name} for {model.collection_name}")

                    if compound_idx.partial:
                        first_field: str = compound_idx.fields[0]

                        field_type: str = "string"
                        if first_field in model_fields:
                            field_info = model_fields[first_field]
                            try:
                                annotation = getattr(field_info, "annotation", None)
                                args = get_args(annotation)
                                field_type = cls._get_field_type(annotation, args)
                            except (AttributeError, TypeError):
                                pass

                        await cls._create_index_with_options(
                            collection=collection,
                            index_fields=index_fields,
                            is_unique=compound_idx.unique,
                            is_sparse=compound_idx.sparse,
                            partial=True,
                            field_type=field_type,
                            index_name=index_name,
                        )
                    else:
                        await cls._create_index_with_options(
                            collection=collection,
                            index_fields=index_fields,
                            is_unique=compound_idx.unique,
                            is_sparse=compound_idx.sparse,
                            partial=False,
                            index_name=index_name,
                        )

        logger.info("MongoDB collections setup completed.")
