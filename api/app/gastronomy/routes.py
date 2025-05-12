from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..gastronomy.crud import (
    create_kitchen,
    get_all_kitchens,
    get_kitchen_by_id,
    remove_kitchen,
    update_kitchen,
)
from ..gastronomy.schemas import (
    KitchenCreate,
    KitchenListResponse,
    KitchenResponse,
    KitchenUpdate,
)
from ..user.crud import is_admin

router = APIRouter()


@router.get("/kitchens/", response_model=KitchenListResponse)
async def get_kitchens(
    session: SessionDep,
    page: int = 1,
    limit: int = 6,
) -> KitchenListResponse:

    return await get_all_kitchens(session=session, page=page, limit=limit)


@router.post("/kitchens/", response_model=KitchenResponse)
async def post_kitchen(
    session: SessionDep,
    kitchen: KitchenCreate,
    _: None = Depends(is_admin),
) -> KitchenResponse:

    return await create_kitchen(session=session, kitchen_create=kitchen)


@router.get("/kitchens/{kitchen_id}/", response_model=KitchenResponse)
async def get_kitchen(
    session: SessionDep,
    kitchen_id: int,
) -> KitchenResponse:

    return await get_kitchen_by_id(session=session, kitchen_id=kitchen_id)


@router.patch("/kitchens/{kitchen_id}/", response_model=KitchenResponse)
async def put_kitchen(
    session: SessionDep,
    kitchen_id: int,
    kitchen: KitchenUpdate,
    _: None = Depends(is_admin),
) -> KitchenResponse:

    return await update_kitchen(
        session=session,
        kitchen_id=kitchen_id,
        kitchen_update=kitchen,
    )


@router.delete("/kitchens/{kitchen_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kitchen(
    session: SessionDep,
    kitchen_id: int,
    _: None = Depends(is_admin),
) -> None:

    await remove_kitchen(session=session, kitchen_id=kitchen_id)
