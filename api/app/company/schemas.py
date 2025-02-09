from typing import Optional

from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    title: str = Field(max_length=100, unique=True, nullable=False, index=True)
    description: str = Field(max_length=255, nullable=False)
    image_link: str = Field(max_length=255, nullable=False)
    rating: float = Field(default=0)

    country_id: Optional[int] = Field(default=None, foreign_key="country.id")
    kitchen_id: Optional[int] = Field(default=None, foreign_key="kitchen.id")


class CompanyResponse(CompanyBase):
    id: int


class CompanyCreate(SQLModel):
    title: str
    description: str
    image_link: str
    country_id: int = 1
    kitchen_id: int = 1


class CompanyUpdate(CompanyCreate):
    pass

class CompanyPatch(SQLModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    image_link: Optional[str] = Field(default=None)
    rating: Optional[float] = Field(default=None)
    country_id: Optional[int] = Field(default=None)
    kitchen_id: Optional[int] = Field(default=None)