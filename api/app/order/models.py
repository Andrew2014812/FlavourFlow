from typing import List, Optional

from sqlmodel import Field, Relationship

from .schemas import OrderBase, OrderItemBase


class Order(OrderBase, table=True):
    __tablename__ = "order"

    id: int = Field(default=None, primary_key=True)

    order_items: List["OrderItem"] = Relationship(back_populates="order")
    user: Optional["User"] = Relationship(back_populates="orders")  # type: ignore


class OrderItem(OrderItemBase, table=True):
    __tablename__ = "order_item"

    id: int = Field(default=None, primary_key=True)

    order: Order = Relationship(back_populates="order_items")
