from sqlmodel import Field, SQLModel


class WishlistBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")


class WishlistItemBase(SQLModel):
    wishlist_id: int = Field(foreign_key="wishlist.id")
    product_id: int = Field(foreign_key="product.id")
    product_title_ua: str
    product_title_en: str
    composition_ua: str
    composition_en: str
    image_link: str
    price: int


class WishlistItemResponse(WishlistItemBase):
    product_id: int
    company_id: int
    id: int


class WishlistItemFullResponse(WishlistItemResponse):
    total_pages: int
