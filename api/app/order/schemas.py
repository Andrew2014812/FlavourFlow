from typing import List

from sqlmodel import Field, SQLModel


class OrderBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    total_price: float


class OrderCreate(SQLModel):
    total_price: float
    order_items: List["OrderItemCreate"]


class OrderItemBase(SQLModel):
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int
