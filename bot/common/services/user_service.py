from enum import Enum
from typing import Optional

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


class UserEndpoints(Enum):
    GET_ME = "users/me/"
    UPDATE_ME = "users/update/me/"
    REGISTER = "users/register/"
    LOGIN = "users/token/"


async def get_user(telegram_id: int) -> Optional[UserResponseMe]:
    user_info = await get_user_info(telegram_id)
    if not user_info or not user_info.is_registered:
        return None
    response = await make_request(
        sub_url=UserEndpoints.GET_ME.value,
        method=APIMethods.GET.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )
    return UserResponseMe.model_validate(response.get("data"))


async def update_user(telegram_id: int, **fields) -> Optional[UserResponseMe]:
    user_info = await get_user_info(telegram_id)
    if not user_info or not user_info.is_registered:
        return None
    response = await make_request(
        sub_url=UserEndpoints.UPDATE_ME.value,
        method=APIMethods.PATCH.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
        body=fields,
    )
    return UserResponseMe.model_validate(response.get("data"))


async def register_user(user_data: UserCreate) -> Optional[UserResponse]:
    response = await make_request(
        sub_url=UserEndpoints.REGISTER.value,
        body=user_data.model_dump(),
        method=APIMethods.POST.value,
    )
    if response.get("status") == status.HTTP_201_CREATED:
        return UserResponse.model_validate(response.get("data"))
    return None


async def login_user(user_data: UserLogin) -> Token:
    response = await make_request(
        sub_url=UserEndpoints.LOGIN.value,
        body=user_data.model_dump(),
        method=APIMethods.POST.value,
    )
    return Token.model_validate(response.get("data"))
