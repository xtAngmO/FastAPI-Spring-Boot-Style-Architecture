from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, Self, TypeVar, cast, overload

from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette.datastructures import State

from src.entities.user_entity import RoleUser
from src.exceptions.forbidden_error import ForbiddenError
from src.exceptions.unauthorized_error import UnauthorizedError
from src.models.user_model import UserResponse
from src.repositories.user_repository import UserRepository
from src.services.jwt_service import JwtService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
jwt_service = JwtService()
user_repository = UserRepository()

T = TypeVar("T")
P = ParamSpec("P")


class SecureState(State):
    def __init__(self: Self) -> None:
        super().__init__()
        self.current_user: UserResponse | None = None


class SecureRequest(Request):
    @property
    def state(self: Self) -> SecureState:
        if not hasattr(self, "_state"):
            self._state = SecureState()
        return self._state


@overload
def jwt_secured(func: Callable[P, T]) -> Callable[P, T]:
    ...


@overload
def jwt_secured(*, role: RoleUser = RoleUser.USER) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


def jwt_secured(
    func: Callable[P, T] | None = None,
    *,
    role: RoleUser = RoleUser.USER,
) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            request = kwargs.get("request")

            if request is None and args and isinstance(args[0], Request):
                request = args[0]

            if not isinstance(request, Request):
                raise TypeError("Request parameter is required and must be of type Request")

            secure_request = SecureRequest(request.scope, request.receive)
            token = await oauth2_scheme(request)

            try:
                payload = jwt_service.decode_token(token)
                user_id = payload.get("uid")
                if not user_id:
                    raise UnauthorizedError(message="Invalid token")

                user = await user_repository.find_by_id(user_id)
                if not user:
                    raise UnauthorizedError(message="User not found")

                if role not in (RoleUser.USER, user.role):
                    raise ForbiddenError(message=f"Access denied. Required role: {role.value}")

                current_user = UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )

                secure_request.state.current_user = current_user

                if args and isinstance(args[0], Request):
                    args_list = list(args)
                    args_list[0] = secure_request
                    args = tuple(args_list)
                elif "request" in kwargs:
                    kwargs["request"] = secure_request

                return await func(*args, **kwargs)

            except JWTError as e:
                raise UnauthorizedError(message="Invalid token") from e

        return cast(Callable[P, T], wrapper)

    if func is None:
        return decorator
    return decorator(func)
