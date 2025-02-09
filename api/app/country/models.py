from typing import List

from sqlmodel import Field, Relationship

from api.app.country.schemas import CountryBase


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    companies: List["Company"] = Relationship(back_populates="country")
