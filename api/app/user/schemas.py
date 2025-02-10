from typing import Optional

import phonenumbers
from fastapi import HTTPException, status
from phonenumbers import NumberParseException
from pydantic import field_validator
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    phone_number: str = Field(unique=True, index=True)
    redactor: str = Field(default='system')
    bonuses: float = Field(default=0)
    telegram_id: int = Field(unique=True, index=True)
    role: str = Field(default='user')


    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value):
        try:
            parsed_number = phonenumbers.parse(value)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid phone number format')


class UserCreate(SQLModel):
    username: str
    phone_number: str
    telegram_id: int
    password: str


class UserResponse(UserBase):
    id: int


class UserLogin(SQLModel):
    username: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: Optional[str] = None
    role: Optional[str] = None
