from enum import Enum

from src.utils.mongo_field import MongoField
from src.utils.mongo_model import MongoBaseModel, collection_name


class RoleUser(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


@collection_name("users")
class UserEntity(MongoBaseModel):
    username: str | None = MongoField[str](
        default=None,
        unique=True,
        partial=True,
        index=True,
        max_length=255,
    )()
    password: str | None = MongoField[str](default=None)()
    name: str | None = MongoField[str](default=None)()
    email: str | None = MongoField[str](
        default=None,
        unique=True,
        partial=True,
        index=True,
        max_length=255,
    )()
    role: RoleUser = MongoField[RoleUser](default=RoleUser.USER, index=True)()


UserEntity.add_compound_index(fields=["role", "username"])
UserEntity.add_compound_index(fields=["role", "email"])
