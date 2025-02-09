import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app.common.database import create_db_and_tables
from api.app.country.routes import router as country_router
from api.app.kitchen.routes import router as kitchen_router
from api.app.user.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, create_db_and_tables)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(country_router, prefix="/country", tags=["countries"])
app.include_router(kitchen_router, prefix="/kitchen", tags=["kitchens"])


@app.get("/")
def read_root() -> dict:
    """
    Simple root endpoint that returns a message.

    Returns:
        dict: {"msg": "Hello World"}
    """
    return {"msg": "Hello World"}
