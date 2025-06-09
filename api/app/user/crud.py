from datetime import datetime, timedelta, timezone
from typing import List

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlmodel import or_, select

from bot.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY

from ..common.dependencies import SessionDep
from ..user.models import User
from ..user.schemas import (
    Token,
    TokenData,
    UserCreate,
    UserLogin,
    UserPatch,
    UserResponse,
    UserResponseMe,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token/")


async def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    statement = select(User).where(
        or_(
            User.phone_number == user.phone_number,
            User.telegram_id == user.telegram_id,
        )
    )
    result = await session.exec(statement)
    existing_user = result.first()

    if existing_user:
        return existing_user

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        telegram_id=int(user.telegram_id),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def update_user(
    session: SessionDep, user_id: int, user_update: UserCreate | UserPatch
) -> UserResponseMe:
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    existing_user = result.first()

    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(existing_user, key, value)

    session.add(existing_user)
    await session.commit()
    await session.refresh(existing_user)

    return existing_user


async def remove_user(session: SessionDep, user_id: int):
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await session.delete(existing_user)
    await session.commit()


async def change_user_role(
    session: SessionDep, user_id: int, role: str
) -> UserResponse:
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_user.role = role

    await session.commit()
    await session.refresh(existing_user)

    return existing_user


async def get_user_by_params(
    session: SessionDep,
    phone_number: str,
    telegram_id: int,
) -> UserResponse | List[UserResponse]:
    if phone_number:
        return await get_user_by_phone(session, phone_number)

    elif telegram_id:
        return await get_by_telegram_id(session, telegram_id)

    else:
        return await get_all_users(session)


async def get_all_users(session: SessionDep) -> List[UserResponse]:
    result = await session.exec(select(User))
    return result.all()


async def get_user_by_phone(session: SessionDep, phone_number: str) -> UserResponse:
    statement = select(User).where(User.phone_number == phone_number)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this phone_number does not exist",
        )

    return UserResponse.model_validate(existing_user)


async def get_user_by_id(session: SessionDep, user_id: int) -> UserResponse:
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id does not exist",
        )

    return UserResponse.model_validate(existing_user)


async def get_by_telegram_id(session: SessionDep, telegram_id: int):
    statement = select(User).where(User.telegram_id == telegram_id)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with telegram id does not exist",
        )

    return UserResponse.model_validate(existing_user)


async def is_authenticated(session: SessionDep, telegram_id: int):
    statement = select(User).where(User.telegram_id == telegram_id)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with telegram id does not exist",
        )

    return True


async def authenticate_user(session: SessionDep, user_login: UserLogin) -> Token:
    statement = select(User).where(User.phone_number == user_login.phone_number)
    result = await session.exec(statement)
    existing_user = result.first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this phone does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={
            "phone_number": existing_user.phone_number,
            "telegram_id": existing_user.telegram_id,
            "role": existing_user.role,
        },
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type="Bearer",
        telegram_id=existing_user.telegram_id,
        user_role=existing_user.role,
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        phone_number: str = payload.get("phone_number")
        role: str = payload.get("role")

        if phone_number is None or role is None:
            raise credentials_exception

        token_data = TokenData(phone_number=phone_number, role=role)

    except PyJWTError:
        raise credentials_exception

    current_user = await get_user_by_phone(
        session, phone_number=token_data.phone_number
    )

    if current_user is None:
        raise credentials_exception

    return current_user


async def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return user
