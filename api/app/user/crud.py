from datetime import datetime, timedelta, timezone
from typing import List

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlmodel import select, or_

from api.app.common.dependencies import SessionDep
from api.app.user.models import User
from api.app.user.schemas import UserCreate, UserResponse, TokenData, Token
from application.config import ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token/")


def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    existing_user = session.exec(
        select(User).where(
            or_(
                User.phone_number == user.phone_number,
                User.username == user.username,
                User.telegram_id == user.telegram_id,
            )
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User with this credentials already registered"
        )

    db_user = User(
        username=user.username,
        phone_number=user.phone_number,
        telegram_id=user.telegram_id,
    )
    db_user.password = user.password

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserResponse.model_validate(db_user)


def get_user_by_params(session: SessionDep,
                       phone_number: str,
                       telegram_id: int,
                       username: str) -> UserResponse | List[UserResponse]:
    if phone_number:
        return get_user_by_phone(session, phone_number)

    elif telegram_id:
        return get_by_telegram_id(session, telegram_id)

    elif username:
        return get_by_username(session, username)

    else:
        return get_all_users(session)


def get_all_users(session: SessionDep) -> List[UserResponse]:
    return session.exec(select(User)).all()


def get_user_by_phone(session: SessionDep, phone_number: str) -> UserResponse:
    existing_user = session.exec(select(User).where(User.phone_number == phone_number)).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this phone_number does not exist"
        )

    return UserResponse.model_validate(existing_user)


def get_user_by_id(session: SessionDep, user_id: int) -> UserResponse:
    existing_user = session.exec(select(User).where(User.id == user_id)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this id does not exist")

    return UserResponse.model_validate(existing_user)


def get_by_telegram_id(session: SessionDep, telegram_id: int):
    existing_user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with telegram id does not exist")

    return UserResponse.model_validate(existing_user)


def get_by_username(session: SessionDep, username: str):
    existing_user = session.exec(select(User).where(User.username == username)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this username does not exist")

    return UserResponse.model_validate(existing_user)


def is_authenticated(session: SessionDep, telegram_id: int):
    existing_user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with telegram id does not exist")

    return True


def change_telegram_id(session: SessionDep, username: str, telegram_id: int):
    existing_user: User = session.exec(select(User).where(User.username == username)).first()
    existing_user.telegram_id = telegram_id


def authenticate_user(session: SessionDep, username: str, password: str) -> Token:
    existing_user = session.exec(select(User).where(User.username == username)).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not existing_user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": existing_user.username, "role": existing_user.role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise credentials_exception

        token_data = TokenData(username=username, role=role)

    except PyJWTError:
        raise credentials_exception

    user = get_by_username(session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
