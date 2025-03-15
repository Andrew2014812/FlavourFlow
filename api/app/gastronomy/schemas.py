from typing import List, Optional

from sqlmodel import Field, SQLModel


class CountryBase(SQLModel):
    title_ua: str = Field(max_length=100, unique=True)
    title_en: str = Field(max_length=100)


class CountryResponse(CountryBase):
    id: int


class CountryListResponse(SQLModel):
    countries: List[CountryResponse]
    total_pages: int


class CountryCreate(CountryBase):
    pass


class CountryUpdate(SQLModel):
    title_en: Optional[str] = None
    title_ua: Optional[str] = None


class KitchenBase(SQLModel):
    title_ua: str = Field(max_length=100, unique=True)
    title_en: str = Field(max_length=100, unique=True)


class KitchenResponse(KitchenBase):
    id: int


class KitchenCreate(KitchenBase):
    pass


class KitchenUpdate(KitchenBase):
    pass


class KitchenListResponse(SQLModel):
    kitchens: List[KitchenResponse]
    total_pages: int
