from typing import Optional

from fastapi import Form
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=255)
    composition: str = Field(max_length=255)
    image_link: str = Field(max_length=255)
    image_id: str = Field(max_length=255)
    product_category: str = Field(max_length=30)
    price: float = Field(default=1)

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")


class ProductCreate(SQLModel):
    title: str
    description: str
    composition: str
    product_category: str
    price: float
    company_id: int = 1

    @classmethod
    def as_form(cls,
                title: str = Form(...),
                description: str = Form(...),
                composition: str = Form(...),
                product_category: str = Form(...),
                price: float = Form(...),
                company_id: int = Form(1)):
        return cls(
            title=title,
            description=description,
            composition=composition,
            product_category=product_category,
            price=price, company_id=company_id
        )


class ProductResponse(ProductBase):
    id: int
