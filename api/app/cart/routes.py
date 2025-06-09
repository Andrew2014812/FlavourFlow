from typing import List

from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..user.crud import get_current_user
from ..user.models import User
from .crud import (
    add_to_cart,
    change_amount,
    clear_cart,
    get_cart_items,
    remove_cart_item,
)
from .schemas import (
    CartItemChangeAmount,
    CartItemCreate,
    CartItemFullResponse,
    CartItemResponse,
)

router = APIRouter()


@router.get("/")
async def get_cart(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    page: int = 1,
    return_all: bool = False,
) -> CartItemFullResponse | List[CartItemResponse] | None:

    return await get_cart_items(
        session=session, user_id=current_user.id, page=page, return_all=return_all
    )


@router.patch("/amount/", status_code=status.HTTP_200_OK)
async def patch_cart_item_amount(
    session: SessionDep,
    item: CartItemChangeAmount,
    _: User = Depends(get_current_user),
) -> None:
    return await change_amount(session=session, item=item)


@router.post("/add/")
async def post_cart_item(
    new_item: CartItemCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> CartItemResponse:

    return await add_to_cart(
        session=session, user_id=current_user.id, new_item=new_item
    )


@router.delete("/remove/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    session: SessionDep,
    item_id: int,
    current_user: User = Depends(get_current_user),
):

    await remove_cart_item(session=session, user_id=current_user.id, item_id=item_id)


@router.delete("/clear/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart_route(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):

    await clear_cart(session=session, user_id=current_user.id)
