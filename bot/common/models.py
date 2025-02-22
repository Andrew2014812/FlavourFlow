from typing import Optional

from sqlalchemy import Column, BigInteger
from sqlmodel import SQLModel, Field


class UserInfo(SQLModel, table=True):
    __tablename__ = "user_info"
    telegram_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    access_token: str = Field(nullable=True)
    token_type: str = Field(nullable=True)
    language_code: Optional[str] = Field(default='en')
    phone_number: Optional[str] = Field(nullable=True)
    is_registered: bool = Field(default=False)
