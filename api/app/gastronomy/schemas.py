from typing import List

from sqlmodel import SQLModel


class KitchenBase(SQLModel):
    title_ua: str
    title_en: str


class KitchenResponse(KitchenBase):
    id: int


class KitchenCreate(KitchenBase):
    pass


class KitchenUpdate(KitchenBase):
    pass


class KitchenListResponse(SQLModel):
    kitchens: List[KitchenResponse]
    total_pages: int
