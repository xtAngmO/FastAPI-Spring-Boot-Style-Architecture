from fastapi import APIRouter, status

from src.configs.security_config import SecureRequest, jwt_secured
from src.dtos.auth_dto import LoginRequest, RegisterRequest
from src.models.auth_model import TokenResponse
from src.models.user_model import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest) -> UserResponse:
    return await AuthService().register(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: LoginRequest) -> TokenResponse:
    return await AuthService().login(user_data.username, user_data.password)


@router.get("/me", response_model=UserResponse)
@jwt_secured
async def get_me(request: SecureRequest) -> UserResponse:
    return request.state.current_user
