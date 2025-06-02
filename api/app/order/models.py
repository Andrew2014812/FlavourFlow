from typing import List, Optional

from sqlmodel import Field, Relationship

from api.app.product.models import Product

from .schemas import OrderBase, OrderItemBase


class Order(OrderBase, table=True):
    __tablename__ = "order"

    id: int = Field(default=None, primary_key=True)
    is_payed: bool = Field(default=False)

    user_id: int = Field(foreign_key="user.id")
    company_id: int = Field(foreign_key="company.id")

    order_items: List["OrderItem"] = Relationship(back_populates="order")
    user: Optional["User"] = Relationship(back_populates="orders")  # type: ignore


class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_item"

    id: int = Field(default=None, primary_key=True)

    order: Order = Relationship(back_populates="order_items")
    product: Product = Relationship(back_populates="order_items")
