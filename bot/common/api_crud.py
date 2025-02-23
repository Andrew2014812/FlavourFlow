from enum import Enum

from fastapi import status

from api.app.user.schemas import UserCreate, Token, UserLogin
from api.app.user.schemas import UserResponseMe, UserResponse
from bot.common.bot_crud import get_user_info
from bot.common.utils import make_request


class APIRequests(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    USER_GET_ME = "users/me/"
    USER_UPDATE_ME = "users/update/me/"
    USER_REGISTER = "users/register/"
    USER_LOGIN = "users/token/"


async def get_user(telegram_id: int) -> UserResponseMe | None:
    user_info = get_user_info(telegram_id)

    if not user_info or not user_info.is_registered:
        return None

    response = await make_request(
        sub_url=APIRequests.USER_GET_ME.value,
        method=APIRequests.GET.value,
        headers={'Authorization': f'{user_info.token_type} {user_info.access_token}'},
    )

    return UserResponseMe.model_validate(response.get('data'))


async def update_user(telegram_id: int, **fields) -> UserResponseMe | None:
    user_info = get_user_info(telegram_id)

    if not user_info or not user_info.is_registered:
        return None

    response = await make_request(
        sub_url=APIRequests.USER_UPDATE_ME.value,
        method=APIRequests.PATCH.value,
        headers={'Authorization': f'{user_info.token_type} {user_info.access_token}'},
        body=fields
    )

    return UserResponseMe.model_validate(response.get('data'))


async def register_user(user_data: UserCreate) -> UserResponse:
    response = await make_request(
        sub_url=APIRequests.USER_REGISTER.value,
        body=user_data.model_dump(),
        method=APIRequests.POST.value
    )

    status_code = response.get('status')
    if status_code == status.HTTP_201_CREATED:
        user = UserResponse.model_validate(response.get('data'))
        return user


async def login_user(user_data: UserLogin):
    response = await make_request(
        sub_url=APIRequests.USER_LOGIN.value,
        body=user_data.model_dump(),
        method=APIRequests.POST.value
    )

    token = Token.model_validate(response.get('data'))

    return token
