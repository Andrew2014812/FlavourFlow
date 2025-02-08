from sqlmodel import Field
from api.app.common.security import get_password_hash, verify_password
from api.app.users.schemas import UserBase


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    @property
    def password(self):
        raise AttributeError("You can't access password attribute")

    @password.setter
    def password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
