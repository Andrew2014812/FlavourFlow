from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str
    email: EmailStr = Field(unique=True, index=True)
    redactor: str
    bonuses: float
    telegram_id: int
    is_admin: bool = Field(default=False)


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class TokenResponse(SQLModel):
    access_token: str
