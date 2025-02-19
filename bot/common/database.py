from sqlmodel import create_engine, SQLModel

from bot.common.models import UserInfo  # noqa
from bot.config import sqlite_path

SQLITE_DATABASE_URL = f"sqlite:///{sqlite_path}"
engine = create_engine(SQLITE_DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
