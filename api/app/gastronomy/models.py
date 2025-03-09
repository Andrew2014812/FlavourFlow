from typing import List

from sqlmodel import Field, Relationship

from api.app.gastronomy.schemas import CountryBase, KitchenBase


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    companies: List["Company"] = Relationship(back_populates="country")


class Kitchen(KitchenBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    companies: List["Company"] = Relationship(back_populates="kitchen")
