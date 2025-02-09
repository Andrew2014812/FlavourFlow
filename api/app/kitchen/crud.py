from typing import List

from fastapi import HTTPException, status

from api.app.common.dependencies import SessionDep
from api.app.kitchen.models import Kitchen
from api.app.kitchen.schemas import KitchenResponse, KitchenCreate


def create_kitchen(session: SessionDep, kitchen: KitchenCreate) -> KitchenResponse:
    existing_kitchen: Kitchen = session.query(Kitchen).filter(Kitchen.title == kitchen.title).first()

    if existing_kitchen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country already exists")

    db_kitchen = Kitchen(title=kitchen.title)

    session.add(db_kitchen)
    session.commit()
    session.refresh(db_kitchen)

    return db_kitchen


def get_kitchen_list(session: SessionDep) -> List[KitchenResponse]:
    kitchen_list: List[KitchenResponse] = session.query(Kitchen).all()
    return kitchen_list


def get_kitchen_by_id(session: SessionDep, country_id: int) -> KitchenResponse:
    existing_kitchen: Kitchen = session.query(Kitchen).filter(Kitchen.id == country_id).first()

    if not existing_kitchen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    return existing_kitchen
