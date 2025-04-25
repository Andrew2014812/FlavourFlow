from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...common.database import engine
from ...common.models import UserInfo


async def get_user_info(telegram_id: int) -> Optional[UserInfo]:
    async with AsyncSession(engine) as session:
        statement = select(UserInfo).where(UserInfo.telegram_id == telegram_id)
        result = await session.exec(statement)
        return result.first()


async def create_user_info(telegram_id: int, language_code: str) -> UserInfo:
    async with AsyncSession(engine) as session:
        user_info = await get_user_info(telegram_id)
        if user_info:
            user_info.language_code = language_code
        else:
            user_info = UserInfo(telegram_id=telegram_id, language_code=language_code)
            session.add(user_info)
        await session.commit()
        await session.refresh(user_info)
        return user_info


async def update_user_info(telegram_id: int, **fields) -> UserInfo:
    async with AsyncSession(engine) as session:
        user_info = await get_user_info(telegram_id)
        if not user_info:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        for key, value in fields.items():
            if not hasattr(user_info, key):
                raise AttributeError(f"Field {key} does not exist")
            setattr(user_info, key, value)

        session.add(user_info)
        await session.commit()
        await session.refresh(user_info)
        return user_info
