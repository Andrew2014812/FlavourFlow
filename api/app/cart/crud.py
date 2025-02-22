from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.cart.models import Cart, CartItem
from api.app.cart.schemas import CartItemCreate, CartItemResponse
from api.app.common.dependencies import SessionDep


def add_to_cart(session: SessionDep, user_id: int, new_item: CartItemCreate) -> CartItemResponse:
    cart = session.exec(select(Cart).filter(Cart.user_id == user_id)).first()

    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)

    cart_item = (
        session.exec(select(CartItem)
                     .filter(CartItem.cart_id == cart.id, CartItem.product_id == new_item.product_id)).first()
    )

    if cart_item:
        cart_item.quantity += cart_item.quantity

    else:
        cart_item = CartItem(cart_id=cart.id, product_id=new_item.product_id, quantity=new_item.quantity)
        session.add(cart_item)

    session.commit()
    session.refresh(cart_item)
    return cart_item


def get_cart_items(session: SessionDep, user_id: int) -> List[CartItemResponse]:
    cart = session.exec(select(Cart).filter(Cart.user_id == user_id)).first()

    if not cart:
        return []

    return cart.items


def get_item_by_id(session: SessionDep, item_id: int) -> CartItemResponse:
    item = session.exec(select(CartItem).filter(CartItem.id == item_id)).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


def remove_cart_item(session: SessionDep, user_id: int, item_id: int):
    cart = session.exec(select(Cart).filter(Cart.user_id == user_id)).first()

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    item_to_delete = get_item_by_id(session, item_id)
    if item_to_delete.cart.telegram_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can delete only your own item")

    session.delete(item_to_delete)
    session.commit()
