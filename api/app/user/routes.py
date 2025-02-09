from fastapi import APIRouter, status, Query

from api.app.common.dependencies import SessionDep
from api.app.user.crud import (
    create_user,
    get_user_by_params,
    get_user_by_id,
    authenticate_user,
)
from api.app.user.schemas import UserLogin, TokenResponse
from ..user.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
def post_user(user: UserCreate, session: SessionDep) -> UserResponse:
    """
    Create a new user in the database.

    Args:
        user (UserCreate): The user to be created
        session (SessionDep): The database session

    Returns:
        UserResponse: The created user
    """

    return create_user(user=user, session=session)


@router.post("/login/")
def user_auth(user: UserLogin, session: SessionDep) -> TokenResponse:
    """
    Authenticate a user and generate a token.

    Args:
        user (UserLogin): The login credentials for the user.
        session (SessionDep): The database session.

    Returns:
        TokenResponse: The authentication token for the user.
    """

    return authenticate_user(user=user, session=session)


@router.get("/")
def retrieve_user(
        session: SessionDep,
        phone_number: str = Query(default=None, description="Filter by phone_number"),
        telegram_id: int = Query(default=None, description="Filter by telegram id"),
        username: str = Query(default=None, description="Filter by username"),
) -> UserResponse:
    """
    Retrieve a user by email, telegram_id, or username.

    Args:
        session (SessionDep): The database session.
        phone_number (str, optional): The phone_number to filter by.
        telegram_id (int, optional): The telegram id to filter by.
        username (str, optional): The username to filter by.

    Returns:
        UserResponse: The retrieved user based on the provided filters.
    """

    return get_user_by_params(
        phone_number=phone_number, telegram_id=telegram_id, username=username, session=session
    )


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
