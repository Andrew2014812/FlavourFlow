from sqlmodel import Field

from api.app.kitchen.schemas import KitchenBase


class Kitchen(KitchenBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
