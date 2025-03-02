from typing import Optional

from fastapi import Form, UploadFile, File
from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    title_ua: str = Field(max_length=100, unique=True, nullable=False, index=True)
    title_en: str = Field(max_length=100, unique=True, nullable=False, index=True)

    description_ua: str = Field(max_length=255, nullable=False)
    description_en: str = Field(max_length=255, nullable=False)

    image_link: str = Field(max_length=255, default="in progress", nullable=True)
    image_id: str = Field(max_length=255, default="in progress", nullable=True)
    rating: float = Field(default=0)

    country_id: int = Field(foreign_key="country.id")
    kitchen_id: int = Field(foreign_key="kitchen.id")


class CompanyResponse(CompanyBase):
    id: int


class CompanyListResponse(SQLModel):
    companies: list[CompanyResponse]
    total_pages: int


class CompanyCreate(SQLModel):
    title_ua: str
    title_en: str

    description_ua: str
    description_en: str

    image: UploadFile = File(...)
    country_id: int = 1
    kitchen_id: int = 1

    @classmethod
    def as_form(
        cls,
        title_ua: str = Form(...),
        title_en: str = Form(...),
        description_ua: str = Form(...),
        description_en: str = Form(...),
        image: Optional[UploadFile] = File(...),
        country_id: int = Form(1),
        kitchen_id: int = Form(1),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            description_ua=description_ua,
            description_en=description_en,
            image=image,
            country_id=country_id,
            kitchen_id=kitchen_id,
        )


class CompanyPatch(SQLModel):
    title_ua: Optional[str] = Field(default=None)
    title_en: Optional[str] = Field(default=None)
    description_ua: Optional[str] = Field(default=None)
    description_en: Optional[str] = Field(default=None)
    image: Optional[UploadFile] = File(default=None)
    rating: Optional[float] = Field(default=None)
    country_id: Optional[int] = Field(default=None)
    kitchen_id: Optional[int] = Field(default=None)

    @classmethod
    def as_form(
        cls,
        title_ua: Optional[str] = Form(None),
        title_en: Optional[str] = Form(None),
        description_ua: Optional[str] = Form(None),
        description_en: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        rating: Optional[float] = Form(None),
        country_id: Optional[int] = Form(None),
        kitchen_id: Optional[int] = Form(None),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            description_ua=description_ua,
            description_en=description_en,
            image=image,
            rating=rating,
            country_id=country_id,
            kitchen_id=kitchen_id,
        )
