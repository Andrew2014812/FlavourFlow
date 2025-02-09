from typing import List

from sqlmodel import Field, Relationship

from api.app.kitchen.schemas import KitchenBase


class Kitchen(KitchenBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    companies: List["Company"] = Relationship(back_populates="country")
