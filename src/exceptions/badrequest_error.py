from typing import Self

from fastapi import status

from src.exceptions.base_error import BaseError


class BadRequestError(BaseError):
    def __init__(self: Self, message: str = "Bad request", code: int = 400):
        super().__init__(message, code, status.HTTP_400_BAD_REQUEST)
