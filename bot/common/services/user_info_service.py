from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.common.database import engine
from bot.common.models import UserInfo


async def get_user_info(telegram_id: int) -> Optional[UserInfo]:
    async with AsyncSession(engine) as session:
        statement = select(UserInfo).where(UserInfo.telegram_id == telegram_id)
        result = await session.exec(statement)
        user_info = result.first()
        return user_info


async def create_user_info(telegram_id: int, language_code: str) -> UserInfo:
    async with AsyncSession(engine) as session:
        existing_user = await get_user_info(telegram_id)

        if existing_user:
            existing_user.language_code = language_code
            await session.commit()
            return existing_user

        user_info = UserInfo(telegram_id=telegram_id, language_code=language_code)
        session.add(user_info)
        await session.commit()
        await session.refresh(user_info)

        return user_info


async def update_user_info(telegram_id: int, **fields) -> UserInfo:
    async with AsyncSession(engine) as session:
        existing_user = await get_user_info(telegram_id)

        if existing_user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        for field_name, new_value in fields.items():
            if not hasattr(existing_user, field_name):
                raise AttributeError(f"Field {field_name} does not exist in user object")

            setattr(existing_user, field_name, new_value)

        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)

        return existing_user
