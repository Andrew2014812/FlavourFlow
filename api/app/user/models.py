from typing import Optional

from sqlmodel import Field, Relationship

from api.app.cart.models import Cart
from api.app.common.security import get_password_hash, verify_password
from api.app.user.schemas import UserBase
from api.app.wishlist.models import Wishlist


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    cart: Optional[Cart] = Relationship(back_populates="user", cascade_delete=True)
    wishlist: Optional[Wishlist] = Relationship(back_populates="user", cascade_delete=True)

    @property
    def password(self):
        raise AttributeError("You can't access password attribute")

    @password.setter
    def password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
