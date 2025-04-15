from typing import Self

from fastapi import status

from src.exceptions.base_error import BaseError


class InternalError(BaseError):
    def __init__(self: Self, message: str = "Internal server error", code: int = 500):
        super().__init__(message, code, status.HTTP_500_INTERNAL_SERVER_ERROR)
