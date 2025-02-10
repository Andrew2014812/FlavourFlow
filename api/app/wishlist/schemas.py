from sqlmodel import Field, SQLModel


class WishlistBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")


class WishlistItemBase(SQLModel):
    wishlist_id: int = Field(foreign_key="wishlist.id")
    product_id: int = Field(foreign_key="product.id")


class WishlistItemCreate(SQLModel):
    product_id: int


class WishlistItemResponse(WishlistItemBase):
    id: int
