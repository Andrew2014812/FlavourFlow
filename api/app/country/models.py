from sqlmodel import Field

from api.app.country.schemas import CountryBase


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
