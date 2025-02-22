from enum import Enum

from fastapi import status

from api.app.user.schemas import UserCreate, Token, UserLogin
from api.app.user.schemas import UserResponse
from bot.common.utils import make_request


class APIRequests(Enum):
    GET = "get"
    POST = "post"
    USER_GET = "users/"
    USER_REGISTER = "users/register/"
    USER_LOGIN = "users/token/"
    AUTH_HEADER = {"Authorization": "Bearer {token}"}


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
