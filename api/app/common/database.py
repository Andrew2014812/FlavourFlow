from sqlmodel import create_engine, SQLModel

import api.app.cart.models  # noqa
import api.app.company.models  # noqa
import api.app.country.models  # noqa
import api.app.kitchen.models  # noqa
import api.app.product.models  # noqa
import api.app.user.models  # noqa
import api.app.wishlist.models  # noqa
from bot.config import PG_DB_NAME, PG_DB_USER, PG_DB_PASSWORD, PG_DB_HOST, PG_DB_PORT

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
