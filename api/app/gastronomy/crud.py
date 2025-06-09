from ..common.dependencies import SessionDep
from .models import Kitchen
from .schemas import KitchenCreate, KitchenListResponse, KitchenResponse, KitchenUpdate
from .service import CuisineCRUDService

kitchen_service = CuisineCRUDService[
    Kitchen, KitchenCreate, KitchenUpdate, KitchenResponse
](Kitchen)


async def get_all_kitchens(
    session: SessionDep,
    page: int = 1,
    limit: int = 6,
) -> KitchenListResponse:
    result = await kitchen_service.get_all(session, page, limit)
    return KitchenListResponse(
        kitchens=result["items"], total_pages=result["total_pages"]
    )


async def create_kitchen(
    session: SessionDep,
    kitchen_create: KitchenCreate,
) -> KitchenResponse:
    return await kitchen_service.create(session, kitchen_create)


async def get_kitchen_by_id(session: SessionDep, kitchen_id: int) -> KitchenResponse:
    return await kitchen_service.get_by_id(session, kitchen_id)


async def update_kitchen(
    session: SessionDep,
    kitchen_id: int,
    kitchen_update: KitchenUpdate,
) -> KitchenResponse:
    return await kitchen_service.update(session, kitchen_id, kitchen_update)


async def remove_kitchen(session: SessionDep, kitchen_id: int) -> None:
    await kitchen_service.delete(session, kitchen_id)
