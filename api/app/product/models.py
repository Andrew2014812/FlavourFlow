from typing import Optional

from sqlmodel import Field, Relationship

from api.app.company.models import Company
from api.app.product.schemas import ProductBase


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    company: Optional[Company] = Relationship(back_populates="products")
