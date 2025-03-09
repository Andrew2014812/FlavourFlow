from typing import List, Optional

from sqlmodel import Field, Relationship

from ..company.schemas import CompanyBase
from ..gastronomy.models import Country, Kitchen


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    country: Optional[Country] = Relationship(back_populates="companies")
    kitchen: Optional[Kitchen] = Relationship(back_populates="companies")
    products: List["Product"] = Relationship(back_populates="company")
