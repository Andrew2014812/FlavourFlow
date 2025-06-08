from typing import List, Optional

from sqlmodel import Field, Relationship

from ..company.schemas import CompanyBase
from ..gastronomy.models import Kitchen


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    kitchen: Optional[Kitchen] = Relationship(back_populates="companies")
    products: List["Product"] = Relationship(back_populates="company")  # type: ignore
    orders: List["Order"] = Relationship(back_populates="company")  # type: ignore
