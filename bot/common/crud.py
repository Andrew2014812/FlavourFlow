from enum import Enum

from sqlmodel import Session, select

from api.app.user.schemas import UserCreate, UserResponse, Token, UserLogin
from bot.common.database import engine
from bot.common.models import UserInfo
from bot.common.utils import make_request


class APIRequests(Enum):
    GET = "get"
    POST = "post"
    USER_REGISTER = "users/register/"
    USER_LOGIN = "users/token/"


async def register_user(user_data: UserCreate):
    response_status, _ = await make_request(APIRequests.USER_REGISTER.value,
                                            user_data.model_dump(),
                                            APIRequests.POST.value)

    if response_status == 201 or response_status == 400:
        user = UserLogin(phone_number=user_data.phone_number)
        return await login_user(user)


async def login_user(user_data: UserLogin):
    _, response_data = await make_request(APIRequests.USER_LOGIN.value,
                                          user_data.model_dump(),
                                          APIRequests.POST.value)

    token = Token.model_validate(response_data)

    return create_user_info(token.telegram_id, token.access_token)


def create_user_info(user_id: int, token: str):
    with Session(engine) as session:
        existing_user = session.exec(select(UserInfo).where(UserInfo.user_id == user_id))

        if existing_user:
            return False

        user_info = UserInfo(user_id=user_id, token=token)
        session.add(user_info)
        session.commit()
        session.close()

        return True
