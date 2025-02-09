from typing import List

from fastapi import APIRouter

from api.app.common.dependencies import SessionDep
from api.app.kitchen.crud import get_kitchen_list, create_kitchen
from api.app.kitchen.schemas import KitchenResponse, KitchenCreate

router = APIRouter()


@router.get("/")
def kitchen_list(session: SessionDep) -> List[KitchenResponse]:
    return get_kitchen_list(session)


@router.post("/")
def post_country(session: SessionDep, country: KitchenCreate) -> KitchenResponse:
    return create_kitchen(session, country)
