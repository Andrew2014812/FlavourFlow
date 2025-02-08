from fastapi import APIRouter, status, Query

from api.app.users.schemas import UserLogin, TokenResponse
from api.app.common.database import SessionDep
from api.app.users.crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    authenticate_user,
)
from ..users.schemas import UserCreate, UserResponse

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
def retrieve_user_by_email(
        session: SessionDep,
        email: str = Query(description="Filter by email"),
) -> UserResponse:
    """
    Retrieve a user by email or id.

    Args:
        session (SessionDep): The database session
        email (str): The email to filter by (optional)

    Returns:
        UserResponse: The retrieved user
    """

    return get_user_by_email(email=email, session=session)


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
