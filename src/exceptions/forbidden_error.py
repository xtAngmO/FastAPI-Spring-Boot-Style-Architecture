from typing import Self

from fastapi import status

from src.exceptions.base_error import BaseError


class ForbiddenError(BaseError):
    def __init__(self: Self, message: str = "Forbidden", code: int = 403):
        super().__init__(message, code, status.HTTP_403_FORBIDDEN)
