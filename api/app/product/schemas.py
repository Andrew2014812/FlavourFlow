from typing import Optional

from fastapi import File, Form, UploadFile
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title_ua: str = Field(max_length=100)
    title_en: str = Field(max_length=100)

    composition_ua: str = Field(max_length=255)
    composition_en: str = Field(max_length=255)

    image_link: str = Field(max_length=255, nullable=True, unique=True)
    image_id: str = Field(max_length=255, nullable=True, unique=True)
    price: str = Field(max_length=255)

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")


class ProductCreate(SQLModel):
    title_ua: str
    title_en: str
    composition_ua: str
    composition_en: str
    price: str
    company_id: int = 1
    image: UploadFile = File(...)

    @classmethod
    def as_form(
        cls,
        title_ua: str = Form(...),
        title_en: str = Form(...),
        composition_ua: str = Form(...),
        composition_en: str = Form(...),
        price: str = Form(...),
        company_id: int = Form(1),
        image: Optional[UploadFile] = File(...),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            composition_ua=composition_ua,
            composition_en=composition_en,
            price=price,
            company_id=company_id,
            image=image,
        )


class ProductResponse(ProductBase):
    id: int


class ProductListResponse(SQLModel):
    products: list[ProductResponse]
    total_pages: int


class ProductPatch(SQLModel):
    title_ua: Optional[str] = Field(default=None)
    title_en: Optional[str] = Field(default=None)
    composition_ua: Optional[str] = Field(default=None)
    composition_en: Optional[str] = Field(default=None)
    price: Optional[str] = Field(default=None)
    image: Optional[UploadFile] = File(default=None)
    company_id: Optional[int] = Field(default=None)

    @classmethod
    def as_form(
        cls,
        title_ua: Optional[str] = Form(None),
        title_en: Optional[str] = Form(None),
        composition_ua: Optional[str] = Form(None),
        composition_en: Optional[str] = Form(None),
        price: Optional[str] = Form(None),
        company_id: Optional[int] = Form(None),
        image: Optional[UploadFile] = File(None),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            composition_ua=composition_ua,
            composition_en=composition_en,
            image=image,
            price=price,
            company_id=company_id,
        )
