from typing import List, Optional

from sqlmodel import Field, Relationship

from ..cart.models import Cart
from ..order.models import Order
from ..user.schemas import UserBase
from ..wishlist.models import Wishlist


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    cart: Optional[Cart] = Relationship(back_populates="user", cascade_delete=True)
    wishlist: Optional[Wishlist] = Relationship(
        back_populates="user", cascade_delete=True
    )
    orders: List[Order] = Relationship(back_populates="user")
