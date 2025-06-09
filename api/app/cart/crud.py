from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..common.dependencies import SessionDep
from ..product.models import Product
from ..utils import get_entity_by_params
from .models import Cart, CartItem
from .schemas import (
    CartItemChangeAmount,
    CartItemCreate,
    CartItemFullResponse,
    CartItemResponse,
)


async def add_to_cart(
    session: SessionDep,
    user_id: int,
    new_item: CartItemCreate,
) -> CartItemResponse:
    cart: Cart = await get_entity_by_params(
        session, Cart, user_id=user_id, options=[joinedload(Cart.company)]
    )

    if cart and new_item.company_id != cart.company.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cart.company.title_en,
        )

    if not cart:
        cart = Cart(user_id=user_id, company_id=new_item.company_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)

    cart_item = await get_entity_by_params(
        session,
        CartItem,
        cart_id=cart.id,
        product_id=new_item.product_id,
    )

    if cart_item:
        return cart_item

    else:
        product: Product = await get_entity_by_params(
            session, Product, id=new_item.product_id
        )
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=new_item.product_id,
            quantity=new_item.quantity,
            price=product.price,
            product_title_ua=product.title_ua,
            product_title_en=product.title_en,
            composition_ua=product.composition_ua,
            composition_en=product.composition_en,
            image_link=product.image_link,
        )
        session.add(cart_item)

    await session.commit()
    await session.refresh(cart_item)

    return cart_item


async def get_cart_items(
    session: SessionDep,
    user_id: int,
    page: int,
    limit: int = 1,
    return_all: bool = False,
) -> CartItemFullResponse | List[CartItemResponse] | None:
    cart: Cart = await get_entity_by_params(
        session, Cart, user_id=user_id, options=[joinedload(Cart.items)]
    )
    if not cart:
        return None

    cart_items, total_pages = await get_entity_by_params(
        session,
        CartItem,
        cart_id=cart.id,
        page=page,
        limit=limit,
        with_total_pages=True,
        order_by="id",
        return_all=True,
    )

    if not cart_items:
        return None

    if return_all:
        return cart.items

    return CartItemFullResponse(**cart_items[0].model_dump(), total_pages=total_pages)


async def get_item_by_id(session: SessionDep, item_id: int) -> CartItemResponse:
    statement = select(CartItem).filter(CartItem.id == item_id)
    result = await session.exec(statement)
    item = result.first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    return item


async def change_amount(session: SessionDep, item: CartItemChangeAmount):
    cart_item: CartItem = await get_entity_by_params(
        session,
        CartItem,
        id=item.item_id,
    )
    if cart_item.quantity == 1 and item.amount < 0:
        return

    cart_item.quantity += item.amount

    await session.commit()


async def remove_cart_item(session: SessionDep, user_id: int, item_id: int):
    cart: Cart = await get_entity_by_params(
        session, Cart, user_id=user_id, options=[joinedload(Cart.items)]
    )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    item_to_delete: CartItem = await get_item_by_id(session, item_id)
    if item_to_delete.cart.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can delete only your own item",
        )

    await session.delete(item_to_delete)
    await session.commit()
    await session.refresh(cart)

    if not cart.items:
        await clear_cart(session=session, user_id=user_id)


async def clear_cart(session: SessionDep, user_id: int):
    cart: Cart = await get_entity_by_params(session, Cart, user_id=user_id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    await session.delete(cart)
    await session.commit()
