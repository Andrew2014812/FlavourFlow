from sqlmodel import Session, select

from bot.common.database import engine
from bot.common.models import UserInfo


def create_user_info(telegram_id: int, language_code: str) -> UserInfo:
    with Session(engine) as session:
        existing_user = session.exec(select(UserInfo).where(UserInfo.telegram_id == telegram_id)).first()

        if existing_user:
            existing_user.language_code = language_code
            session.commit()
            return existing_user

        user_info = UserInfo(telegram_id=telegram_id, language_code=language_code)
        session.add(user_info)
        session.commit()
        session.refresh(user_info)

        return user_info


def get_user_info(telegram_id: int) -> UserInfo:
    with Session(engine) as session:
        user_info = session.exec(select(UserInfo).where(UserInfo.telegram_id == telegram_id)).first()
        return user_info


def update_user_info(telegram_id: int, **fields) -> UserInfo:
    with Session(engine) as session:
        existing_user = get_user_info(telegram_id)

        if existing_user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        for field_name, new_value in fields.items():
            if not hasattr(existing_user, field_name):
                raise AttributeError(f"Field {field_name} does not exist in user object")

            setattr(existing_user, field_name, new_value)

        session.add(existing_user)
        session.commit()
        session.refresh(existing_user)

        return existing_user
