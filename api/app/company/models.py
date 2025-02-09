from typing import Optional

from sqlmodel import Field, Relationship

from api.app.company.schemas import CompanyBase
from api.app.country.models import Country
from api.app.kitchen.models import Kitchen


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    country: Optional[Country] = Relationship(back_populates="companies")
    kitchen: Optional[Kitchen] = Relationship(back_populates="companies")
