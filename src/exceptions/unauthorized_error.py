from typing import Self

from fastapi import status

from src.exceptions.base_error import BaseError


class UnauthorizedError(BaseError):
    def __init__(self: Self, message: str = "unauthorized", code: int = 401):
        super().__init__(message, code, status.HTTP_401_UNAUTHORIZED)
