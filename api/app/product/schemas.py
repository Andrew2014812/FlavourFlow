from typing import Optional

from fastapi import Form, UploadFile, File
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title_ua: str = Field(max_length=100)
    title_en: str = Field(max_length=100)

    description_ua: str = Field(max_length=255)
    description_en: str = Field(max_length=255)

    composition_ua: str = Field(max_length=255)
    composition_en: str = Field(max_length=255)

    image_link: str = Field(max_length=255, nullable=True, unique=True)
    image_id: str = Field(max_length=255, nullable=True, unique=True)
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
    image: UploadFile = File(...)

    @classmethod
    def as_form(cls,
                title: str = Form(...),
                description: str = Form(...),
                composition: str = Form(...),
                product_category: str = Form(...),
                price: float = Form(...),
                company_id: int = Form(1),
                image: UploadFile = File(...)):
        return cls(
            title=title,
            description=description,
            composition=composition,
            product_category=product_category,
            price=price,
            company_id=company_id,
            image=image
        )


class ProductResponse(ProductBase):
    id: int


class ProductPatch(SQLModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    composition: Optional[str] = Field(default=None)
    product_category: Optional[str] = Field(default=None)
    price: Optional[float] = Field(default=None)
    image: Optional[UploadFile] = File(default=None)
    company_id: Optional[int] = Field(default=None)

    @classmethod
    def as_form(
            cls,
            title: Optional[str] = Form(None),
            description: Optional[str] = Form(None),
            composition: Optional[str] = Form(None),
            product_category: Optional[str] = Form(None),
            price: Optional[float] = Form(None),
            company_id: Optional[int] = Form(None),
            image: Optional[UploadFile] = File(None),
    ):
        return cls(
            title=title,
            description=description,
            composition=composition,
            image=image,
            product_category=product_category,
            price=price,
            company_id=company_id,
        )
