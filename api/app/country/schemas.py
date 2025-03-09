from sqlmodel import Field, SQLModel


class CountryBase(SQLModel):
    title_ua: str = Field(max_length=100, unique=True)
    title_en: str = Field(max_length=100)


class CountryResponse(CountryBase):
    id: int


class CountryListResponse(SQLModel):
    countries: list[CountryResponse]
    total_pages: int


class CountryCreate(CountryBase):
    pass


class CountryUpdate(CountryBase):
    pass
