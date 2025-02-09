from typing import Optional

from fastapi import Form, UploadFile, File
from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    title: str = Field(max_length=100, unique=True, nullable=False, index=True)
    description: str = Field(max_length=255, nullable=False)
    image_link: str = Field(max_length=255, nullable=False)
    image_id: str = Field(max_length=255, nullable=False)
    rating: float = Field(default=0)

    country_id: Optional[int] = Field(default=None, foreign_key="country.id")
    kitchen_id: Optional[int] = Field(default=None, foreign_key="kitchen.id")


class CompanyResponse(CompanyBase):
    id: int


class CompanyCreate(SQLModel):
    title: str
    description: str
    image: Optional[UploadFile] = File(...)
    country_id: int = 1
    kitchen_id: int = 1


    @classmethod
    def as_form(cls,
                title: str = Form(...),
                description: str = Form(...),
                image: Optional[UploadFile] = File(...),
                country_id: int = Form(1),
                kitchen_id: int = Form(1)):
        return cls(
            title=title,
            description=description,
            image=image,
            country_id=country_id,
            kitchen_id=kitchen_id
        )

class CompanyPatch(SQLModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    image: Optional[UploadFile] = File(default=None)
    rating: Optional[float] = Field(default=None)
    country_id: Optional[int] = Field(default=None)
    kitchen_id: Optional[int] = Field(default=None)

    @classmethod
    def as_form(
            cls,
            title: Optional[str] = Form(None),
            description: Optional[str] = Form(None),
            image: Optional[UploadFile] = File(None),
            rating: Optional[float] = Form(None),
            country_id: Optional[int] = Form(None),
            kitchen_id: Optional[int] = Form(None),
    ):
        return cls(
            title=title,
            description=description,
            image=image,
            rating=rating,
            country_id=country_id,
            kitchen_id=kitchen_id,
        )