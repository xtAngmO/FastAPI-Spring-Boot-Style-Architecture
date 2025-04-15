from typing import Self

from fastapi import status

from src.exceptions.base_error import BaseError


class NotFoundError(BaseError):
    def __init__(self: Self, message: str = "Not found error", code: int = 404):
        super().__init__(message, code, status.HTTP_404_NOT_FOUND)
