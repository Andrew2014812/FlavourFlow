from typing import List

from fastapi import APIRouter, Depends, Query, status

from ..common.dependencies import SessionDep
from ..user.crud import (
    authenticate_user,
    change_user_role,
    create_user,
    get_current_user,
    get_user_by_id,
    get_user_by_params,
    is_admin,
    remove_user,
    update_user,
)
from ..user.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserPatch,
    UserResponse,
    UserResponseMe,
    UserRole,
)

router = APIRouter()


@router.get("/")
async def retrieve_user(
    session: SessionDep,
    phone_number: str = Query(default=None, description="Filter by phone_number"),
    telegram_id: int = Query(default=None, description="Filter by telegram id"),
    _: None = Depends(is_admin),
) -> UserResponse | List[UserResponse]:

    return await get_user_by_params(
        phone_number=phone_number,
        telegram_id=telegram_id,
        session=session,
    )


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def post_user(user: UserCreate, session: SessionDep) -> UserResponse:

    return await create_user(session=session, user=user)


@router.get("/me/")
async def get_me(
    current_user: UserResponseMe = Depends(get_current_user),
) -> UserResponseMe:
    return current_user


@router.put("/update/me/", status_code=status.HTTP_200_OK)
async def put_user(
    session: SessionDep,
    user: UserCreate,
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    return await update_user(session=session, user_update=user, user_id=current_user.id)


@router.patch("/update/me/", status_code=status.HTTP_200_OK)
async def put_user(
    session: SessionDep,
    user: UserPatch,
    current_user: UserResponseMe = Depends(get_current_user),
) -> UserResponseMe:
    return await update_user(session=session, user_update=user, user_id=current_user.id)


@router.put("/update", status_code=status.HTTP_200_OK)
async def put_user_via_admin(
    user_id: int, session: SessionDep, user: UserCreate, _: None = Depends(is_admin)
) -> UserResponse:
    return await update_user(session=session, user_update=user, user_id=user_id)


@router.patch("/update", status_code=status.HTTP_200_OK)
async def patch_user_via_admin(
    user_id: int,
    session: SessionDep,
    user: UserPatch,
    _: None = Depends(is_admin),
) -> UserResponse:
    return await update_user(session=session, user_update=user, user_id=user_id)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: SessionDep,
    _: None = Depends(is_admin),
):
    await remove_user(session=session, user_id=user_id)


@router.post("/token/")
async def login_for_access_token(
    session: SessionDep,
    user: UserLogin,
) -> Token:

    return await authenticate_user(session, user)


@router.get("/{user_id}/")
async def retrieve_user_by_id(user_id: int, session: SessionDep) -> UserResponse:

    return await get_user_by_id(user_id=user_id, session=session)


@router.post("/promote/")
async def promote_user(
    user_id: int,
    session: SessionDep,
    _: None = Depends(is_admin),
) -> UserResponse:
    return await change_user_role(
        session=session, user_id=user_id, role=UserRole.ADMIN.value
    )


@router.post("/demote/")
async def demote_user(
    user_id: int,
    session: SessionDep,
    _: None = Depends(is_admin),
) -> UserResponse:
    return await change_user_role(
        session=session, user_id=user_id, role=UserRole.USER.value
    )
