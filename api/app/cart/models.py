from typing import Optional, List

from sqlmodel import Relationship, Field

from api.app.cart.schemas import CartBase, CartItemBase


class Cart(CartBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    items: List["CartItem"] = Relationship(back_populates="cart", cascade_delete=True)
    user: Optional["User"] = Relationship(back_populates="cart")


class CartItem(CartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    cart: Optional[Cart] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")
