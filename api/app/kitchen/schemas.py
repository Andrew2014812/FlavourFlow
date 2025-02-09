from sqlmodel import Field, SQLModel


class KitchenBase(SQLModel):
    title: str = Field(max_length=100, unique=True)


class KitchenResponse(KitchenBase):
    id: int


class KitchenCreate(KitchenBase):
    pass


class KitchenUpdate(KitchenBase):
    pass
