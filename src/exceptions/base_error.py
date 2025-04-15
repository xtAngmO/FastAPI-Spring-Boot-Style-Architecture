from typing import Self

from fastapi import status


class BaseError(Exception):
    def __init__(self: Self, message: str, code: int, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)
