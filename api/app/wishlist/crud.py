from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.wishlist.models import Wishlist, WishlistItem
from api.app.wishlist.schemas import WishlistItemCreate, WishlistItemResponse


async def add_to_wishlist(
        session: SessionDep,
        user_id: int,
        new_item: WishlistItemCreate,
) -> WishlistItemResponse | dict:
    statement = select(Wishlist).filter(Wishlist.user_id == user_id)
    result = await session.exec(statement)
    wishlist = result.first()

    if not wishlist:
        wishlist = Wishlist(user_id=user_id)
        session.add(wishlist)
        await session.commit()
        await session.refresh(wishlist)

    statement = select(WishlistItem).filter(
        WishlistItem.wishlist_id == wishlist.id,
        WishlistItem.product_id == new_item.product_id
    )

    result = await session.exec(statement)
    wishlist_item = result.first()

    if wishlist_item:
        session.delete(wishlist_item)
        session.commit()
        return {'msg': 'Item removed'}

    else:
        wishlist_item = WishlistItem(wishlist_id=wishlist.id, product_id=new_item.product_id)
        session.add(wishlist_item)

    await session.commit()
    await session.refresh(wishlist_item)

    return wishlist_item


async def get_wishlist_items(session: SessionDep, user_id: int) -> List[WishlistItemResponse]:
    statement = select(Wishlist).filter(Wishlist.user_id == user_id)
    result = await session.exec(statement)
    wishlist = result.first()

    if not wishlist:
        return []

    return wishlist.items


async def get_item_by_id(session: SessionDep, item_id: int) -> WishlistItemResponse:
    statement = select(WishlistItem).filter(WishlistItem.id == item_id)
    result = await session.exec(statement)
    item = result.first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


async def remove_wishlist_item(session: SessionDep, user_id: int, item_id: int):
    statement = select(Wishlist).filter(Wishlist.user_id == user_id)
    result = await session.exec(statement)
    wishlist = result.first()

    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found")

    item_to_delete = await get_item_by_id(session, item_id)
    if item_to_delete.wishlist.telegram_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can delete only your own item")

    await session.delete(item_to_delete)
    await session.commit()
    await session.refresh(wishlist)
