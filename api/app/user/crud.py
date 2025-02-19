from datetime import datetime, timedelta, timezone
from typing import List

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlmodel import select, or_

from api.app.common.dependencies import SessionDep
from api.app.user.models import User
from api.app.user.schemas import UserCreate, UserResponse, TokenData, Token, UserPatch, UserLogin
from bot.config import JWT_ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token/")


def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    existing_user = session.exec(
        select(User).where(
            or_(
                User.phone_number == user.phone_number,
                User.telegram_id == user.telegram_id,
            )
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this credentials already registered",
        )

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        telegram_id=int(user.telegram_id),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def update_user(session: SessionDep, user_id: int, user_update: UserCreate | UserPatch) -> UserResponse:
    existing_user = session.exec(select(User).where(User.id == user_id)).first()

    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(existing_user, key, value)

    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)

    return existing_user


def remove_user(session: SessionDep, user_id: int):
    existing_user = session.exec(select(User).where(User.id == user_id)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(existing_user)
    session.commit()


def change_user_role(session: SessionDep, user_id: int, role: str) -> UserResponse:
    existing_user = session.exec(select(User).where(User.id == user_id)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_user.role = role

    session.commit()
    session.refresh(existing_user)

    return existing_user


def get_user_by_params(
        session: SessionDep,
        phone_number: str,
        telegram_id: int,
) -> UserResponse | List[UserResponse]:
    if phone_number:
        return get_user_by_phone(session, phone_number)

    elif telegram_id:
        return get_by_telegram_id(session, telegram_id)

    else:
        return get_all_users(session)


def get_all_users(session: SessionDep) -> List[UserResponse]:
    return session.exec(select(User)).all()


def get_user_by_phone(session: SessionDep, phone_number: str) -> UserResponse:
    existing_user = session.exec(
        select(User).where(User.phone_number == phone_number)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this phone_number does not exist",
        )

    return UserResponse.model_validate(existing_user)


def get_user_by_id(session: SessionDep, user_id: int) -> UserResponse:
    existing_user = session.exec(select(User).where(User.id == user_id)).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this id does not exist",
        )

    return UserResponse.model_validate(existing_user)


def get_by_telegram_id(session: SessionDep, telegram_id: int):
    existing_user = session.exec(
        select(User).where(User.telegram_id == telegram_id)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with telegram id does not exist",
        )

    return UserResponse.model_validate(existing_user)


def is_authenticated(session: SessionDep, telegram_id: int):
    existing_user = session.exec(
        select(User).where(User.telegram_id == telegram_id)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with telegram id does not exist",
        )

    return True


def authenticate_user(session: SessionDep, user_login: UserLogin) -> Token:
    existing_user: User = session.exec(select(User).where(User.phone_number == user_login.phone_number)).first()

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
            "role": existing_user.role,
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


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

    current_user = get_user_by_phone(session, phone_number=token_data.phone_number)

    if current_user is None:
        raise credentials_exception

    return current_user


def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return user
