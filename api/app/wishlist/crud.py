from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.wishlist.models import Wishlist, WishlistItem
from api.app.wishlist.schemas import WishlistItemCreate, WishlistItemResponse


def add_to_wishlist(session: SessionDep, user_id: int, new_item: WishlistItemCreate) -> WishlistItemResponse | dict:
    wishlist = session.exec(select(Wishlist).filter(Wishlist.user_id == user_id)).first()

    if not wishlist:
        wishlist = Wishlist(user_id=user_id)
        session.add(wishlist)
        session.commit()
        session.refresh(wishlist)

    wishlist_item = (
        session.exec(select(WishlistItem)
                     .filter(WishlistItem.wishlist_id == wishlist.id,
                             WishlistItem.product_id == new_item.product_id)).first()
    )

    if wishlist_item:
        session.delete(wishlist_item)
        session.commit()
        return {'msg': 'Item removed'}

    else:
        wishlist_item = WishlistItem(wishlist_id=wishlist.id, product_id=new_item.product_id)
        session.add(wishlist_item)

    session.commit()
    session.refresh(wishlist_item)
    return wishlist_item


def get_wishlist_items(session: SessionDep, user_id: int) -> List[WishlistItemResponse]:
    wishlist = session.exec(select(Wishlist).filter(Wishlist.user_id == user_id)).first()

    if not wishlist:
        return []

    return wishlist.items


def get_item_by_id(session: SessionDep, item_id: int) -> WishlistItemResponse:
    item = session.exec(select(WishlistItem).filter(WishlistItem.id == item_id)).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


def remove_wishlist_item(session: SessionDep, user_id: int, item_id: int):
    wishlist = session.exec(select(Wishlist).filter(Wishlist.user_id == user_id)).first()

    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found")

    item_to_delete = get_item_by_id(session, item_id)
    if item_to_delete.wishlist.telegram_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can delete only your own item")

    session.delete(item_to_delete)
    session.commit()
    session.refresh(wishlist)
