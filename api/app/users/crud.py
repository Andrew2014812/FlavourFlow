from fastapi import HTTPException, status
from sqlmodel import select

from api.app.users.models import User
from api.app.users.schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from api.app.common.database import SessionDep


def create_user(session: SessionDep, user: UserCreate) -> UserResponse:
    existing_user = session.exec(select(User).where(User.email == user.email)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already registered"
        )

    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
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
