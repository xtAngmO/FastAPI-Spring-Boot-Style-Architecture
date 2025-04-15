from datetime import datetime

from pydantic import BaseModel

from src.entities.user_entity import RoleUser


class UserResponse(BaseModel):
    id: str
    username: str
    email: str | None
    role: RoleUser
    created_at: datetime
    updated_at: datetime
