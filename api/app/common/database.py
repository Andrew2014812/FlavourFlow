from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlmodel import SQLModel

from api.app.cart.models import Cart
from api.app.company.models import Company
from api.app.country.models import Country
from api.app.kitchen.models import Kitchen
from api.app.product.models import Product
from api.app.user.models import User
from api.app.wishlist.models import Wishlist, WishlistItem
from bot.config import PG_DB_HOST, PG_DB_NAME, PG_DB_PASSWORD, PG_DB_PORT, PG_DB_USER

Cart_model = Cart
Company_model = Company
Country_model = Country
Kitchen_model = Kitchen
Product_model = Product
User_model = User
Wishlist_model = Wishlist
WishlistItem_model = WishlistItem

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
