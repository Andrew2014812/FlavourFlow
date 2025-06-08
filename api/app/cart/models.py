from typing import List, Optional

from sqlmodel import Field, Relationship

from ..company.models import Company
from .schemas import CartBase, CartItemBase


class Cart(CartBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    items: List["CartItem"] = Relationship(back_populates="cart", cascade_delete=True)
    user: Optional["User"] = Relationship(back_populates="cart")  # type: ignore
    company: Optional[Company] = Relationship(back_populates="carts")


class CartItem(CartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    cart: Optional[Cart] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")  # type: ignore
