from enum import Enum
from typing import Optional, Union

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    first_name: str
    last_name: str = Field(nullable=True)
    phone_number: str = Field(unique=True, index=True)
    bonuses: float = Field(default=0)
    telegram_id: int = Field(unique=True, index=True)
    role: str = Field(default='user')


class UserCreate(SQLModel):
    first_name: str
    last_name: Optional[str] = Field(default=None)
    phone_number: str
    telegram_id: int

class UserLogin(SQLModel):
    phone_number: str


class UserResponse(UserBase):
    id: int


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


class TokenData(SQLModel):
    phone_number: Optional[str] = None
    role: Optional[str] = None
