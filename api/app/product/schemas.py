from typing import Optional

from fastapi import UploadFile
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=255)
    composition: str = Field(max_length=255)
    image_link: str = Field(max_length=255)
    product_category: str = Field(max_length=30)
    price: float = Field(default=1)

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")


class ProductCreate(SQLModel):
    title: str
    description: str
    composition: str
    image: UploadFile = Field(...)
    product_category: str
    price: float
    company_id: int = 1
