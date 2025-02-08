import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.app.common.database import create_db_and_tables
from api.app.users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, create_db_and_tables)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/users", tags=["users"])


@app.get("/")
def read_root() -> dict:
    """
    Simple root endpoint that returns a message.

    Returns:
        dict: {"msg": "Hello World"}
    """
    return {"msg": "Hello World"}
