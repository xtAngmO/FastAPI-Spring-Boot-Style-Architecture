from datetime import UTC, datetime, timedelta
from typing import Self

from jose import jwt
from jose.constants import ALGORITHMS

from src.configs.config import get_settings

settings = get_settings()


class JwtService:
    def create_access_token(self: Self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(tz=UTC) + expires_delta
        else:
            expire = datetime.now(tz=UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})

        return jwt.encode(
            claims=to_encode,
            key=settings.JWT_PRIVATE_KEY,
            algorithm=ALGORITHMS.RS256,
        )

    def decode_token(self: Self, token: str) -> dict:
        return jwt.decode(
            token=token,
            key=settings.JWT_PUBLIC_KEY,
            algorithms=[ALGORITHMS.RS256],
        )
