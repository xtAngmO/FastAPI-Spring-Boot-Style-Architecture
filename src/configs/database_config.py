from typing import Optional, Self, TypeVar, cast

import motor.motor_asyncio
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from src.configs.config import get_settings
from src.configs.logging_config import logger
from src.utils.mongo_model import MongoBaseModel
from src.utils.mongo_setup import MongoSetup

T = TypeVar("T", bound=MongoBaseModel)
IndexField = tuple[str, int]
IndexFields = list[IndexField]


class MongoDB:
    _instance: Optional["MongoDB"] = None
    _client: AsyncIOMotorClient | None = None
    _database: AsyncIOMotorDatabase | None = None
    _initialized: bool = False

    def __new__(cls: type[Self]) -> "MongoDB":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connect()
        return cls._instance

    @classmethod
    def _connect(cls: type[Self]) -> None:
        if cls._initialized:
            return

        settings = get_settings()
        cls._client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        cls._database = cls._client[settings.DATABASE_NAME]
        logger.info(f"Connected to MongoDB success, database: {settings.DATABASE_NAME}")
        cls._initialized = True

    @classmethod
    def get_database(cls: type[Self]) -> AsyncIOMotorDatabase:
        if cls._database is None:
            cls._connect()
        return cast(AsyncIOMotorDatabase, cls._database)

    @classmethod
    def get_collection(cls: type[Self], collection_name: str) -> AsyncIOMotorCollection:
        return cls.get_database()[collection_name]

    @classmethod
    async def ping(cls: type[Self]) -> bool:
        try:
            if cls._client:
                await cls._client.admin.command("ping")
            else:
                return False
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
            return False
        else:
            return True

    @classmethod
    async def close_connection(cls: type[Self]) -> None:
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._database = None
            cls._initialized = False
            logger.info("MongoDB connection closed")

    @classmethod
    async def ensure_collections(cls: type[Self]) -> None:
        await MongoSetup()._ensure_collections_exist(cls.get_database())
