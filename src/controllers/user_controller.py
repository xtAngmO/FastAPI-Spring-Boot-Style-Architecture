from fastapi import APIRouter, Query

from src.configs.security_config import SecureRequest, jwt_secured
from src.entities.user_entity import RoleUser
from src.models.user_model import UserResponse
from src.services.user_service import UserService
from src.utils.data_pagination import PaginatedResponse

router = APIRouter(prefix="/users")


@router.get("", response_model=PaginatedResponse[UserResponse])
@jwt_secured(role=RoleUser.ADMIN)
async def get_users(
    request: SecureRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    return await UserService().get_all_users(skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
@jwt_secured(role=RoleUser.ADMIN)
async def get_user(request: SecureRequest, user_id: str) -> UserResponse:
    return await UserService().get_user_by_id(user_id)
