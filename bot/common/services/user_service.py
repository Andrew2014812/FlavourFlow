from enum import Enum

from fastapi import status

from api.app.user.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserResponseMe,
)

from ...config import APIAuth, APIMethods
from ..services.user_info_service import get_user_info
from ..utils import make_request

user_prefix = "users"


class UserEndpoints(Enum):
    USER_GET_ME = f"{user_prefix}/me/"
    USER_UPDATE_ME = f"{user_prefix}/update/me/"
    USER_REGISTER = f"{user_prefix}/register/"
    USER_LOGIN = f"{user_prefix}/token/"


async def get_user(telegram_id: int) -> UserResponseMe | None:
    user_info = await get_user_info(telegram_id)

    if not user_info or not user_info.is_registered:
        return None

    response = await make_request(
        sub_url=UserEndpoints.USER_GET_ME.value,
        method=APIMethods.GET.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return UserResponseMe.model_validate(response.get("data"))


async def update_user(telegram_id: int, **fields) -> UserResponseMe | None:
    user_info = await get_user_info(telegram_id)

    if not user_info or not user_info.is_registered:
        return None

    response = await make_request(
        sub_url=UserEndpoints.USER_UPDATE_ME.value,
        method=APIMethods.PATCH.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
        body=fields,
    )

    return UserResponseMe.model_validate(response.get("data"))


async def register_user(user_data: UserCreate) -> UserResponse:
    response = await make_request(
        sub_url=UserEndpoints.USER_REGISTER.value,
        body=user_data.model_dump(),
        method=APIMethods.POST.value,
    )

    status_code = response.get("status")
    if status_code == status.HTTP_201_CREATED:
        user = UserResponse.model_validate(response.get("data"))
        return user


async def login_user(user_data: UserLogin) -> Token:
    response = await make_request(
        sub_url=UserEndpoints.USER_LOGIN.value,
        body=user_data.model_dump(),
        method=APIMethods.POST.value,
    )

    token = Token.model_validate(response.get("data"))

    return token
