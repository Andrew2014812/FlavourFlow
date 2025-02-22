from enum import Enum

from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.app.user.schemas import UserCreate, Token, UserLogin
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

    if response_status == status.HTTP_201_CREATED or response_status == status.HTTP_400_BAD_REQUEST:
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
        existing_user = session.exec(select(UserInfo).where(UserInfo.user_id == user_id)).first()

        if existing_user:
            return False

        try:
            user_info = UserInfo(user_id=user_id, token=token)
            session.add(user_info)
            session.commit()

        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()

        return True
