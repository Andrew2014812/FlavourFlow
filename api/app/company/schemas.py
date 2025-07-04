from typing import Optional

from fastapi import File, Form, UploadFile
from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    title_ua: str
    title_en: str

    description_ua: str
    description_en: str

    image_link: str = Field(max_length=255, default="in progress", nullable=True)
    image_id: str = Field(max_length=255, default="in progress", nullable=True)

    kitchen_id: int = Field(foreign_key="kitchen.id")


class CompanyResponse(CompanyBase):
    id: int


class CompanyListResponse(SQLModel):
    companys: list[CompanyResponse]
    total_pages: int


class CompanyCreate(SQLModel):
    title_ua: str
    title_en: str

    description_ua: str
    description_en: str

    image: UploadFile = File(...)
    kitchen_id: int = 1

    @classmethod
    def as_form(
        cls,
        title_ua: str = Form(...),
        title_en: str = Form(...),
        description_ua: str = Form(...),
        description_en: str = Form(...),
        image: Optional[UploadFile] = File(...),
        kitchen_id: int = Form(1),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            description_ua=description_ua,
            description_en=description_en,
            image=image,
            kitchen_id=kitchen_id,
        )


class CompanyPatch(SQLModel):
    title_ua: Optional[str] = Field(default=None)
    title_en: Optional[str] = Field(default=None)
    description_ua: Optional[str] = Field(default=None)
    description_en: Optional[str] = Field(default=None)
    image: Optional[UploadFile] = File(default=None)
    kitchen_id: Optional[int] = Field(default=None)

    @classmethod
    def as_form(
        cls,
        title_ua: Optional[str] = Form(None),
        title_en: Optional[str] = Form(None),
        description_ua: Optional[str] = Form(None),
        description_en: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        kitchen_id: Optional[int] = Form(None),
    ):
        return cls(
            title_ua=title_ua,
            title_en=title_en,
            description_ua=description_ua,
            description_en=description_en,
            image=image,
            kitchen_id=kitchen_id,
        )
