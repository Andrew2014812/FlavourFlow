from sqlmodel import Field, SQLModel


class CountryBase(SQLModel):
    title: str = Field(max_length=100, unique=True)


class CountryResponse(CountryBase):
    id: int


class CountryCreate(CountryBase):
    pass


class CountryUpdate(CountryBase):
    pass
