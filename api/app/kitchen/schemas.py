from sqlmodel import Field, SQLModel


class KitchenBase(SQLModel):
    title_ua: str = Field(max_length=100, unique=True)
    title_en: str = Field(max_length=100, unique=True)


class KitchenResponse(KitchenBase):
    id: int


class KitchenCreate(KitchenBase):
    pass


class KitchenUpdate(KitchenBase):
    pass
