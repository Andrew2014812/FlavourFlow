from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    first_name: str
    last_name: Optional[str] = Field(nullable=True, default=None)
    phone_number: str = Field(unique=True, index=True)
    telegram_id: int = Field(sa_column=Column(BigInteger))
    role: Optional[str] = Field(default="user")


class UserCreate(SQLModel):
    first_name: str
    last_name: Optional[str] = Field(default=None)
    phone_number: str
    telegram_id: int


class UserLogin(SQLModel):
    phone_number: str


class UserResponse(UserBase):
    id: int


class UserResponseMe(SQLModel):
    first_name: str
    last_name: Optional[str] = None
    phone_number: str
    telegram_id: int
    role: str


class UserPatch(UserCreate):
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    telegram_id: Optional[int] = Field(default=None)


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class Token(SQLModel):
    access_token: str
    token_type: str
    telegram_id: int
    user_role: str


class TokenData(SQLModel):
    phone_number: Optional[str] = None
    role: Optional[str] = None
