from typing import List

from fastapi import APIRouter, status, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.app.common.dependencies import SessionDep
from api.app.user.crud import (
    create_user,
    get_user_by_params,
    get_user_by_id,
    authenticate_user,
    is_admin,
    get_current_user,
)
from api.app.user.schemas import Token
from .models import User
from ..user.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
def post_user(user: UserCreate, session: SessionDep) -> UserResponse:
    """
    Create a new user

    Args:
        user (UserCreate): The user data to register
        session (SessionDep): The database session

    Returns:
        UserResponse: The created user
    """

    return create_user(user=user, session=session)


@router.get("/")
def retrieve_user(
        session: SessionDep,
        phone_number: str = Query(default=None, description="Filter by phone_number"),
        telegram_id: int = Query(default=None, description="Filter by telegram id"),
        username: str = Query(default=None, description="Filter by username"),
) -> UserResponse | List[UserResponse]:
    """
    Retrieve a user or list of users by optional filters phone_number, telegram_id, or username.

    Args:
        session (SessionDep): The database session
        phone_number (str): Filter by phone_number
        telegram_id (int): Filter by telegram id
        username (str): Filter by username

    Returns:
        UserResponse | List[UserResponse]: The retrieved user(s)
    """

    return get_user_by_params(
        phone_number=phone_number,
        telegram_id=telegram_id,
        username=username,
        session=session,
    )


@router.get("/admin/")
async def admin_endpoint(current_user: User = Depends(is_admin)):
    return {"message": "This is an admin-only endpoint", "user": current_user.username}


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/token/")
async def login_for_access_token(
        session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    Login to retrieve an access token.

    Args:
        session (SessionDep): The database session
        form_data (OAuth2PasswordRequestForm): The username and password to authenticate

    Returns:
        Token: The access token
    """

    return authenticate_user(session, form_data.username, form_data.password)


@router.get("/{user_id}/")
def retrieve_user_by_id(user_id: int, session: SessionDep) -> UserResponse:
    """
    Retrieve a user by id.

    Args:
        user_id (int): The id of the user to retrieve
        session (SessionDep): The database session

    Returns:
        UserResponse: The retrieved user
    """

    return get_user_by_id(user_id=user_id, session=session)
