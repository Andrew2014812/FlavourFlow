from typing import List

from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..user.crud import get_current_user
from ..user.models import User
from .crud import (
    add_to_wishlist,
    get_wishlist_items,
    move_to_cart,
    remove_wishlist_item,
)
from .schemas import WishlistItemFullResponse, WishlistItemResponse

router = APIRouter()


@router.get("/")
async def get_wishlist(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    page: int = 1,
    return_all: bool = False,
) -> WishlistItemFullResponse | List[WishlistItemResponse] | None:

    return await get_wishlist_items(
        session=session, user_id=current_user.id, page=page, return_all=return_all
    )


@router.post("/add/{product_id}/")
async def post_wishlist_item(
    product_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> WishlistItemResponse:

    return await add_to_wishlist(
        session=session,
        user_id=current_user.id,
        product_id=product_id,
    )


@router.delete("/remove/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wishlist_item(
    session: SessionDep,
    item_id: int,
    current_user: User = Depends(get_current_user),
):
    await remove_wishlist_item(
        session=session, user_id=current_user.id, item_id=item_id
    )


@router.put("/move/{item_id}/")
async def move_to_cart_route(
    session: SessionDep,
    item_id: int,
    current_user: User = Depends(get_current_user),
):
    await move_to_cart(
        session=session,
        user_id=current_user.id,
        item_id=item_id,
    )
