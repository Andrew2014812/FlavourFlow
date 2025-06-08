from typing import List, Optional

from sqlmodel import Field, SQLModel

from ..company.models import Company
from ..product.schemas import ProductResponse
from ..user.models import User


class OrderBase(SQLModel):
    total_price: float
    address: str
    time: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List["OrderItemCreate"]


class OrderResponse(OrderBase):
    id: int
    is_submitted: bool = False
    order_items: List["OrderItemResponse"] = []
    user: User = None
    company: Company = None


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
