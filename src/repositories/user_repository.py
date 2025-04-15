from typing import Self

from src.entities.user_entity import UserEntity
from src.utils.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    def __init__(self: Self) -> None:
        super().__init__(UserEntity)

    async def find_by_username(self: Self, username: str) -> UserEntity | None:
        return await self.find_one_by_filter({"username": username})

    async def find_by_username_and_email(self: Self, username: str, email: str | None) -> UserEntity | None:
        filter_conditions = [
            {"username": username},
        ]

        if email:
            filter_conditions.append(
                {"email": email},
            )

        return await self.find_one_by_filter(
            {"$or": filter_conditions},
        )

    async def find_by_username_or_email(self: Self, username_or_email: str) -> UserEntity | None:
        filter_conditions = [
            {"username": username_or_email},
            {"email": username_or_email},
        ]
        return await self.find_one_by_filter(
            {"$or": filter_conditions},
        )
