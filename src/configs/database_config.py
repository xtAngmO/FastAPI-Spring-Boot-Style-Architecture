from typing import Self

import motor.motor_asyncio
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from src.configs.config import get_settings
from src.configs.logging_config import logger


class MongoDB:
    _instance = None
    _client: AsyncIOMotorClient | None = None
    _database = None

    def __new__(cls: type[Self]) -> "MongoDB":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connect()

        return cls._instance

    @classmethod
    def _connect(cls: type[Self]) -> None:
        settings = get_settings()
        cls._client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        cls._database = cls._client[settings.DATABASE_NAME]
        logger.info(f"Connected to MongoDB at Success, database: {settings.DATABASE_NAME}")

    @classmethod
    def get_database(cls: type[Self]) -> AsyncIOMotorDatabase | None:
        if cls._database is None:
            cls._connect()
        return cls._database

    @classmethod
    def get_collection(cls: type[Self], collection_name: str) -> AsyncIOMotorCollection:
        return cls.get_database()[collection_name]

    @classmethod
    async def ping(cls: type[Self]) -> bool:
        try:
            await cls._client.admin.command("ping")
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
            logger.info("MongoDB connection closed")
