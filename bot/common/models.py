from sqlmodel import SQLModel, Field


class UserInfo(SQLModel, table=True):
    __tablename__ = "user_info"
    user_id: int = Field(primary_key=True)
    token: str
