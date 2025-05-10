from sqlmodel import Field, SQLModel


class CartBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")


class CartItemBase(SQLModel):
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)
    product_title_ua: str
    product_title_en: str
    composition_ua: str
    composition_en: str
    image_link: str
    price: str


class CartItemCreate(SQLModel):
    product_id: int
    quantity: int


class CartItemResponse(CartItemBase):
    id: int


class CartItemFullResponse(CartItemResponse):
    total_pages: int


class CartItemChangeAmount(SQLModel):
    item_id: int
    amount: int