from enum import Enum

from pydantic import EmailStr, Field

from src.utils.mongo_model import MongoBaseModel, collection_name


class RoleUser(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


@collection_name("users")
class UserEntity(MongoBaseModel):
    username: str
    password: str
    name: str | None = Field(None)
    email: EmailStr | None = Field(None)
    role: RoleUser = Field(default=RoleUser.USER)
