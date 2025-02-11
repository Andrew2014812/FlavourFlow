from typing import Optional, List

from sqlmodel import Relationship, Field

from api.app.wishlist.schemas import WishlistBase, WishlistItemBase


class Wishlist(WishlistBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    items: List["WishlistItem"] = Relationship(back_populates="wishlist", cascade_delete=True)
    user: Optional["User"] = Relationship(back_populates="wishlist")


class WishlistItem(WishlistItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    wishlist: Optional[Wishlist] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="wishlist_items")
