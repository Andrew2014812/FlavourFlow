from api.app.common.dependencies import SessionDep

from .models import Country, Kitchen
from .schemas import (
    CountryCreate,
    CountryListResponse,
    CountryResponse,
    CountryUpdate,
    KitchenCreate,
    KitchenListResponse,
    KitchenResponse,
    KitchenUpdate,
)
from .service import CuisineCRUDService

country_service = CuisineCRUDService[
    Country, CountryCreate, CountryUpdate, CountryResponse
](Country)
kitchen_service = CuisineCRUDService[
    Kitchen, KitchenCreate, KitchenUpdate, KitchenResponse
](Kitchen)


async def create_country(
    session: SessionDep, country_create: CountryCreate
) -> CountryResponse:
    return await country_service.create(session, country_create)


async def get_all_countries(
    session: SessionDep, page: int = 1, limit: int = 6
) -> CountryListResponse:
    result = await country_service.get_all(session, page, limit)
    return CountryListResponse(
        countries=result["items"], total_pages=result["total_pages"]
    )


async def get_country_by_id(session: SessionDep, country_id: int) -> CountryResponse:
    return await country_service.get_by_id(session, country_id)


async def update_country(
    session: SessionDep, country_id: int, country_update: CountryUpdate
) -> CountryResponse:
    return await country_service.update(session, country_id, country_update)


async def remove_country(session: SessionDep, country_id: int) -> None:
    await country_service.delete(session, country_id)


async def create_kitchen(
    session: SessionDep, kitchen_create: KitchenCreate
) -> KitchenResponse:
    return await kitchen_service.create(session, kitchen_create)


async def get_all_kitchens(
    session: SessionDep, page: int = 1, limit: int = 6
) -> KitchenListResponse:
    result = await kitchen_service.get_all(session, page, limit)
    return KitchenListResponse(
        kitchens=result["items"], total_pages=result["total_pages"]
    )


async def get_kitchen_by_id(session: SessionDep, kitchen_id: int) -> KitchenResponse:
    return await kitchen_service.get_by_id(session, kitchen_id)


async def update_kitchen(
    session: SessionDep, kitchen_id: int, kitchen_update: KitchenUpdate
) -> KitchenResponse:
    return await kitchen_service.update(session, kitchen_id, kitchen_update)


async def remove_kitchen(session: SessionDep, kitchen_id: int) -> None:
    await kitchen_service.delete(session, kitchen_id)
