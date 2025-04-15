from typing import Self

from src.dtos.auth_dto import RegisterRequest
from src.entities.user_entity import UserEntity
from src.exceptions.notfound_error import NotFoundError
from src.models.user_model import UserResponse
from src.repositories.user_repository import UserRepository
from src.utils.data_pagination import PaginatedResponse


class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    async def get_all_users(self: Self, skip: int = 0, limit: int = 100) -> PaginatedResponse:
        return await self.user_repository.find_all(skip, limit)

    async def get_user_by_id(self: Self, id: str) -> UserEntity | None:
        user = await self.user_repository.find_by_id(id)
        if not user:
            raise NotFoundError(
                message=f"User with ID {id} not found",
            )
        return user

    async def find_by_username(self: Self, username: str) -> UserEntity | None:
        user = await self.user_repository.find_by_username(username)
        if not user:
            return None
        return user

    async def create_user(self: Self, register_req: RegisterRequest, hash_password: str) -> UserResponse:
        new_user = UserEntity(
            username=register_req.username,
            password=hash_password,
            email=register_req.email,
            name=register_req.name,
        )
        created_user = await self.user_repository.create(new_user)
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            role=created_user.role,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )
