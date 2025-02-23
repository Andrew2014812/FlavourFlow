from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.kitchen.models import Kitchen
from api.app.kitchen.schemas import KitchenResponse, KitchenCreate, KitchenUpdate


def create_kitchen(session: SessionDep, kitchen_create: KitchenCreate) -> KitchenResponse:
    statement = select(Kitchen).filter(
        Kitchen.title_ua == kitchen_create.title_ua,
        Kitchen.title_en == kitchen_create.title_en
    )

    existing_kitchen: Kitchen = session.exec(statement).first()

    if existing_kitchen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kitchen already exists")

    db_kitchen = Kitchen()

    for key, value in kitchen_create.model_dump().items():
        setattr(db_kitchen, key, value)

    session.add(db_kitchen)
    session.commit()
    session.refresh(db_kitchen)

    return db_kitchen


def get_kitchen_list(session: SessionDep) -> List[KitchenResponse]:
    kitchen_list: List[KitchenResponse] = session.exec(select(Kitchen)).all()
    return kitchen_list


def get_kitchen_by_id(session: SessionDep, kitchen_id: int) -> KitchenResponse:
    existing_kitchen: Kitchen = session.exec(select(Kitchen).filter(Kitchen.id == kitchen_id)).first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    return existing_kitchen


def update_kitchen(session: SessionDep, kitchen_id: int, kitchen_update: KitchenUpdate) -> KitchenResponse:
    existing_kitchen = session.exec(select(Kitchen).filter(Kitchen.id == kitchen_id)).first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    for key, value in kitchen_update.model_dump().items():
        setattr(existing_kitchen, key, value)

    session.merge(existing_kitchen)
    session.commit()
    session.refresh(existing_kitchen)

    return existing_kitchen


def remove_kitchen(session: SessionDep, kitchen_id: int):
    existing_kitchen: Kitchen = session.exec(select(Kitchen).filter(Kitchen.id == kitchen_id)).first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kitchen not found")

    session.delete(existing_kitchen)
    session.commit()
