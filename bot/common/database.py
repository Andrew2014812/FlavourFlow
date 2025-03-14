from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from ..common.models import UserInfo
from ..config import sqlite_path

USER_INFO = UserInfo

SQLITE_DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_path}"
engine = create_async_engine(SQLITE_DATABASE_URL)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
