from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(unique=True, index=True)


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class TokenResponse(SQLModel):
    access_token: str
