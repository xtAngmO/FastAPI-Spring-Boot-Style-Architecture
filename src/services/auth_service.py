from datetime import timedelta
from typing import Self

import bcrypt

from src.configs.config import get_settings
from src.dtos.auth_dto import RegisterRequest
from src.entities.user_entity import UserEntity
from src.exceptions.badrequest_error import BadRequestError
from src.exceptions.unauthorized_error import UnauthorizedError
from src.models.auth_model import TokenResponse
from src.models.user_model import UserResponse
from src.repositories.user_repository import UserRepository
from src.services.jwt_service import JwtService
from src.services.user_service import UserService
from src.utils.validators import validate_email_format

settings = get_settings()


class AuthService:
    def __init__(self: Self) -> None:
        self.user_service = UserService()
        self.jwt_service = JwtService()
        self.user_repository = UserRepository()

    def _hash_password(self: Self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self: Self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def sign_token(self: Self, user: UserEntity, expires: timedelta) -> str:
        data = {
            "sub": "",
            "uid": user.id,
            "email": user.email,
        }
        return self.jwt_service.create_access_token(
            data=data,
            expires_delta=expires,
        )

    async def register(self: Self, register_req: RegisterRequest) -> UserResponse:
        register_req.email = validate_email_format(register_req.email)
        existing_user = await self.user_repository.find_by_username_and_email(register_req.username, register_req.email)
        if existing_user:
            raise BadRequestError("Username or email already exists")

        return await self.user_service.create_user(
            register_req,
            self._hash_password(register_req.password),
        )

    async def login(self: Self, username: str, password: str) -> TokenResponse:
        user = await self.user_repository.find_by_username_or_email(username)
        if not user:
            raise UnauthorizedError(message="Incorrect username")
        try:
            if not self.verify_password(password, user.password):
                raise UnauthorizedError(message="Incorrect password")
        except Exception as e:
            raise UnauthorizedError(message=f"{e}") from e

        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.sign_token(user, access_token_expires)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )
