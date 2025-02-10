import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app.cart.routes import router as cart_router
from api.app.common.database import create_db_and_tables
from api.app.company.routes import router as company_router
from api.app.country.routes import router as country_router
from api.app.kitchen.routes import router as kitchen_router
from api.app.product.routes import router as product_router
from api.app.wishlist.routes import router as wishlist_router
from api.app.user.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, create_db_and_tables)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["user"])
app.include_router(country_router, prefix="/country", tags=["country"])
app.include_router(kitchen_router, prefix="/kitchen", tags=["kitchen"])
app.include_router(company_router, prefix="/company", tags=["company"])
app.include_router(product_router, prefix="/product", tags=["product"])
app.include_router(cart_router, prefix="/cart", tags=["card"])
app.include_router(wishlist_router, prefix="/wishlist", tags=["wishlist"])


@app.get("/")
def read_root() -> dict:
    """
    Simple root endpoint that returns a message.

    Returns:
        dict: {"msg": "Hello World"}
    """
    return {"msg": "Hello World"}
