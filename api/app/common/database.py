from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlmodel import SQLModel

from bot.config import PG_DB_HOST, PG_DB_NAME, PG_DB_PASSWORD, PG_DB_PORT, PG_DB_USER

from ..cart.models import Cart
from ..company.models import Company
from ..gastronomy.models import Kitchen
from ..order.models import Order, OrderItem
from ..product.models import Product
from ..user.models import User
from ..wishlist.models import Wishlist, WishlistItem

Cart_model = Cart
Company_model = Company
Kitchen_model = Kitchen
Product_model = Product
User_model = User
Wishlist_model = Wishlist
WishlistItem_model = WishlistItem
Order_model = Order
OrderItem_model = OrderItem

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{PG_DB_USER}:{PG_DB_PASSWORD}@{PG_DB_HOST}:{PG_DB_PORT}/{PG_DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
