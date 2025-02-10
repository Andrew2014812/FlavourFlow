from sqlmodel import Field, SQLModel


class CartBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")


class CartItemBase(SQLModel):
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)


class CartItemCreate(SQLModel):
    product_id: int
    quantity: int


class CartItemResponse(CartItemBase):
    id: int
