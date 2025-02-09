from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=255)
    image_link: str = Field(max_length=255)
    rating: float = Field(default=0)
