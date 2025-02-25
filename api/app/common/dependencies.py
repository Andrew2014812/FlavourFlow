from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from api.app.common.database import engine


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
