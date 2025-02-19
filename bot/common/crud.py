import asyncio
from enum import Enum

from sqlmodel import Session

from api.app.user.schemas import UserCreate, UserResponse, Token
from bot.common.database import engine
from bot.common.models import UserInfo
from bot.common.utils import make_request


class APIRequests(Enum):
    GET = "get"
    POST = "post"
    USER_REGISTER = "users/register/"
    USER_LOGIN = "users/token/"


async def register_user(user_data: UserCreate):
    response = await make_request(APIRequests.USER_REGISTER.value, user_data.model_dump(), APIRequests.POST.value)

    if response:
        user = UserResponse.model_validate(response)
        await login_user(user)


async def login_user(user_data: UserResponse):
    response = await make_request(APIRequests.USER_LOGIN.value,
                                  user_data.model_dump(include={"phone_number"}),
                                  APIRequests.POST.value)

    token = Token.model_validate(response)

    create_user_info(user_data.telegram_id, token.access_token)


def create_user_info(user_id: int, token: str):
    with Session(engine) as session:
        user_info = UserInfo(user_id=user_id, token=token)
        session.add(user_info)
        session.commit()
        session.close()