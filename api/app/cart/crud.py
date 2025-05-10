from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from ..common.dependencies import SessionDep
from .models import Cart, CartItem
from .schemas import CartItemCreate, CartItemResponse


async def add_to_cart(
    session: SessionDep,
    user_id: int,
    new_item: CartItemCreate,
) -> CartItemResponse:
    statement = select(Cart).filter(Cart.user_id == user_id)
    result = await session.exec(statement)
    cart: Cart = result.first()

    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)

    statement = select(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == new_item.product_id
    )
    result = await session.exec(statement)
    cart_item: CartItem = result.first()

    if cart_item:
        return cart_item

    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=new_item.product_id, quantity=new_item.quantity
        )
        session.add(cart_item)

    await session.commit()
    await session.refresh(cart_item)

    return cart_item


async def get_cart_items(session: SessionDep, user_id: int) -> List[CartItemResponse]:
    statement = select(Cart).filter(Cart.user_id == user_id)
    result = await session.exec(statement)
    cart: Cart = result.first()

    if not cart:
        return []

    return cart.items


async def get_item_by_id(session: SessionDep, item_id: int) -> CartItemResponse:
    statement = select(CartItem).filter(CartItem.id == item_id)
    result = await session.exec(statement)
    item = result.first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    return item


async def remove_cart_item(session: SessionDep, user_id: int, item_id: int):
    statement = select(Cart).filter(Cart.user_id == user_id)
    result = await session.exec(statement)
    cart: Cart = result.first()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    item_to_delete = await get_item_by_id(session, item_id)
    if item_to_delete.cart.telegram_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can delete only your own item",
        )

    await session.delete(item_to_delete)
    await session.commit()
