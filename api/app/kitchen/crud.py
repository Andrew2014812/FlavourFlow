from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.kitchen.models import Kitchen
from api.app.kitchen.schemas import KitchenResponse, KitchenCreate, KitchenUpdate


async def create_kitchen(session: SessionDep, kitchen_create: KitchenCreate) -> KitchenResponse:
    statement = select(Kitchen).filter(
        Kitchen.title_ua == kitchen_create.title_ua,
        Kitchen.title_en == kitchen_create.title_en
    )

    result = await session.exec(statement)
    existing_kitchen = result.first()

    if existing_kitchen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kitchen already exists")

    db_kitchen = Kitchen()

    for key, value in kitchen_create.model_dump().items():
        setattr(db_kitchen, key, value)

    session.add(db_kitchen)
    await session.commit()
    await session.refresh(db_kitchen)

    return db_kitchen


async def get_kitchen_list(session: SessionDep) -> List[KitchenResponse]:
    result = await session.exec(select(Kitchen))
    return result.all()


async def get_kitchen_by_id(session: SessionDep, kitchen_id: int) -> KitchenResponse:
    statement = select(Kitchen).filter(Kitchen.id == kitchen_id)
    result = await session.exec(statement)
    existing_kitchen: Kitchen = result.first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    return existing_kitchen


async def update_kitchen(session: SessionDep, kitchen_id: int, kitchen_update: KitchenUpdate) -> KitchenResponse:
    statement = select(Kitchen).filter(Kitchen.id == kitchen_id)
    result = await session.exec(statement)
    existing_kitchen: Kitchen = result.first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    for key, value in kitchen_update.model_dump().items():
        setattr(existing_kitchen, key, value)

    await session.merge(existing_kitchen)
    await session.commit()
    await session.refresh(existing_kitchen)

    return existing_kitchen


async def remove_kitchen(session: SessionDep, kitchen_id: int):
    statement = select(Kitchen).filter(Kitchen.id == kitchen_id)
    result = await session.exec(statement)
    existing_kitchen: Kitchen = result.first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    await session.delete(existing_kitchen)
    await session.commit()
