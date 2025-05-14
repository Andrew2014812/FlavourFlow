from typing import List, Optional

from sqlmodel import Field, SQLModel

from ..product.schemas import ProductResponse


class OrderBase(SQLModel):
    total_price: float
    address: str
    time: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List["OrderItemCreate"]


class OrderResponse(OrderBase):
    id: int
    order_items: List["OrderItemResponse"] = []


class OrderItemBase(SQLModel):
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int


class OrderItemResponse(OrderItemBase):
    id: int
    product: ProductResponse


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int
