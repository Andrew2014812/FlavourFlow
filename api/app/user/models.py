from typing import Optional

from sqlmodel import Field, Relationship

from api.app.cart.models import Cart
from api.app.user.schemas import UserBase
from api.app.wishlist.models import Wishlist


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    cart: Optional[Cart] = Relationship(back_populates="user", cascade_delete=True)
    wishlist: Optional[Wishlist] = Relationship(back_populates="user", cascade_delete=True)
