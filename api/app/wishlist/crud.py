from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..cart.crud import add_to_cart
from ..cart.schemas import CartItemCreate
from ..common.dependencies import SessionDep
from ..product.models import Product
from ..utils import get_entity_by_params
from .models import Wishlist, WishlistItem
from .schemas import WishlistItemFullResponse, WishlistItemResponse


async def add_to_wishlist(
    session: SessionDep,
    user_id: int,
    product_id: int,
) -> WishlistItemResponse:
    wishlist = await get_entity_by_params(session, Wishlist, user_id=user_id)

    if not wishlist:
        wishlist = Wishlist(user_id=user_id)
        session.add(wishlist)
        await session.commit()
        await session.refresh(wishlist)

    wishlist_item = await get_entity_by_params(
        session,
        WishlistItem,
        wishlist_id=wishlist.id,
        product_id=product_id,
    )

    if wishlist_item:
        return wishlist_item

    else:
        product: Product = await get_entity_by_params(session, Product, id=product_id)
        wishlist_item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=product_id,
            price=product.price,
            product_title_ua=product.title_ua,
            product_title_en=product.title_en,
            composition_ua=product.composition_ua,
            composition_en=product.composition_en,
            image_link=product.image_link,
        )
        session.add(wishlist_item)

    await session.commit()
    await session.refresh(wishlist_item)

    return wishlist_item


async def get_wishlist_items(
    session: SessionDep,
    user_id: int,
    page: int,
    limit: int = 1,
    return_all: bool = False,
) -> WishlistItemFullResponse | List[WishlistItemResponse] | None:
    wishlist: Wishlist = await get_entity_by_params(
        session, Wishlist, user_id=user_id, options=[joinedload(Wishlist.items)]
    )
    if not wishlist:
        return None

    wishlist_items, total_pages = await get_entity_by_params(
        session,
        WishlistItem,
        wishlist_id=wishlist.id,
        page=page,
        limit=limit,
        with_total_pages=True,
        order_by="id",
        return_all=True,
    )

    if not wishlist_items:
        return None

    if return_all:
        return wishlist.items

    return WishlistItemFullResponse(
        **wishlist_items[0].model_dump(), total_pages=total_pages
    )


async def get_item_by_id(session: SessionDep, item_id: int) -> WishlistItemResponse:
    statement = select(WishlistItem).filter(WishlistItem.id == item_id)
    result = await session.exec(statement)
    item = result.first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    return item


async def remove_wishlist_item(session: SessionDep, user_id: int, item_id: int):
    wishlist: Wishlist = await get_entity_by_params(session, Wishlist, user_id=user_id)

    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found"
        )

    item_to_delete: WishlistItem = await get_item_by_id(session, item_id)
    if item_to_delete.wishlist.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can delete only your own item",
        )

    await session.delete(item_to_delete)
    await session.commit()


async def move_to_cart(session: SessionDep, user_id: int, item_id: int):
    wish_list_item: WishlistItem = await get_entity_by_params(
        session, WishlistItem, id=item_id
    )
    cart_item = await add_to_cart(
        new_item=CartItemCreate(product_id=wish_list_item.product_id, quantity=1),
        session=session,
        user_id=user_id,
    )

    if cart_item:
        await remove_wishlist_item(session, user_id, item_id)
