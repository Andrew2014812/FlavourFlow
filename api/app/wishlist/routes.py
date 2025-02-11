from typing import List

from fastapi import APIRouter, Depends

from api.app.common.dependencies import SessionDep
from api.app.user.crud import get_current_user
from api.app.user.models import User
from api.app.wishlist.crud import add_to_wishlist, get_wishlist_items, remove_wishlist_item
from api.app.wishlist.schemas import WishlistItemCreate, WishlistItemResponse

router = APIRouter()


@router.get("/")
def get_cart(
        session: SessionDep,
        current_user: User = Depends(get_current_user),
) -> List[WishlistItemResponse]:
    return get_wishlist_items(session=session, user_id=current_user.id)


@router.post("/add/")
def post_cart_item(
        new_item: WishlistItemCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_user),
) -> WishlistItemResponse | dict:
    return add_to_wishlist(session=session, user_id=current_user.id, new_item=new_item)


@router.delete("/remove/{item_id}")
def delete_cart_item(
        session: SessionDep,
        item_id: int,
        current_user: User = Depends(get_current_user),
) -> dict:
    return remove_wishlist_item(session=session, user_id=current_user.id, item_id=item_id)
