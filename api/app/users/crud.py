from fastapi import HTTPException, status
from sqlmodel import select, func

from api.app.common.dependencies import SessionDep
from api.app.users.models import User
from api.app.users.schemas import UserCreate, UserResponse, UserLogin, TokenResponse


def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    existing_user = session.exec(select(User).where(User.email == user.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already registered"
        )

    db_user = User(
        username=user.username,
        email=user.email,
        redactor=user.redactor,
        bonuses=user.bonuses,
        telegram_id=user.telegram_id,
    )
    db_user.password = user.password

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserResponse.model_validate(db_user)


def authenticate_user(session: SessionDep, user: UserLogin) -> TokenResponse:
    existing_user = session.exec(select(User).where(User.email == user.email)).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist"
        )

    if not existing_user.verify_password(user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    return TokenResponse(access_token='Test')


def get_user_by_email(session: SessionDep, email: str) -> UserResponse:
    existing_user = session.exec(select(User).where(User.email == email)).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist"
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


def is_admin(session: SessionDep, telegram_id: int):
    existing_user: User = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with telegram id does not exist")

    return existing_user.is_admin


def change_telegram_id(session: SessionDep, username: str, telegram_id: int):
    existing_user: User = session.exec(select(User).where(User.username == username)).first()
    existing_user.telegram_id = telegram_id


def is_username_already_exists(session: SessionDep, username: str):
    existing_user = session.exec(select(User).where(User.username == username)).first()

    return True if existing_user is not None else False


def is_email_already_exists(session: SessionDep, email: str):
    existing_user = session.exec(select(User).where(User.email == email)).first()

    return True if existing_user is not None else False


def get_max_id(session: SessionDep):
    return session.exec(select(func.max(User.id))).scalar()