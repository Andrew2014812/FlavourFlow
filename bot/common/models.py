from sqlmodel import SQLModel, Field


class UserInfo(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    token: str
