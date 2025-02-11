from enum import Enum
from typing import Optional

import phonenumbers
from fastapi import HTTPException, status
from pydantic import field_validator
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    phone_number: str = Field(unique=True, index=True)
    bonuses: float = Field(default=0)
    telegram_id: int = Field(unique=True, index=True)
    role: str = Field(default='user')


class UserCreate(SQLModel):
    username: str
    phone_number: str
    telegram_id: int
    password: str

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value):
        try:
            parsed_number = phonenumbers.parse(value)

            if not phonenumbers.is_valid_number(parsed_number):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid phone number')

            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid phone number')


class UserResponse(UserBase):
    id: int


class UserLogin(SQLModel):
    username: str
    password: str


class UserPatch(UserCreate):
    username: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    telegram_id: Optional[int] = Field(default=None)
    password: Optional[str] = Field(default=None)


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: Optional[str] = None
    role: Optional[str] = None
