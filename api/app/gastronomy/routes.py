from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..gastronomy.crud import (
    create_country,
    create_kitchen,
    get_all_countries,
    get_all_kitchens,
    get_country_by_id,
    get_kitchen_by_id,
    remove_country,
    remove_kitchen,
    update_country,
    update_kitchen,
)
from ..gastronomy.schemas import (
    CountryCreate,
    CountryListResponse,
    CountryResponse,
    CountryUpdate,
    KitchenCreate,
    KitchenListResponse,
    KitchenResponse,
    KitchenUpdate,
)
from ..user.crud import is_admin

router = APIRouter()


@router.get("/countries/", response_model=CountryListResponse)
async def get_countries(
    session: SessionDep,
    page: int = 1,
    limit: int = 6,
) -> CountryListResponse:
    """
    Retrieve a list of all countries with pagination.

    Args:
        session (SessionDep): The database session.
        page (int): The page number (default is 1).
        limit (int): The number of items per page (default is 6).

    Returns:
        CountryListResponse: A paginated list of country details.
    """
    return await get_all_countries(session=session, page=page, limit=limit)


@router.get("/kitchens/", response_model=KitchenListResponse)
async def get_kitchens(
    session: SessionDep,
    page: int = 1,
    limit: int = 6,
) -> KitchenListResponse:
    """
    Retrieve a list of all kitchens with pagination.

    Args:
        session (SessionDep): The database session.
        page (int): The page number (default is 1).
        limit (int): The number of items per page (default is 6).

    Returns:
        KitchenListResponse: A paginated list of kitchen details.
    """
    return await get_all_kitchens(session=session, page=page, limit=limit)


@router.post("/countries/", response_model=CountryResponse)
async def post_country(
    session: SessionDep,
    country: CountryCreate,
    _: None = Depends(is_admin),
) -> CountryResponse:
    """
    Create a new country in the database.

    Args:
        session (SessionDep): The database session.
        country (CountryCreate): The country to be created.

    Returns:
        CountryResponse: The created country.
    """
    return await create_country(session=session, country_create=country)


@router.post("/kitchens/", response_model=KitchenResponse)
async def post_kitchen(
    session: SessionDep,
    kitchen: KitchenCreate,
    _: None = Depends(is_admin),
) -> KitchenResponse:
    """
    Create a new kitchen in the database.

    Args:
        session (SessionDep): The database session.
        kitchen (KitchenCreate): The kitchen to be created.

    Returns:
        KitchenResponse: The created kitchen.
    """
    return await create_kitchen(session=session, kitchen_create=kitchen)


@router.get("/countries/{country_id}/", response_model=CountryResponse)
async def get_country(
    session: SessionDep,
    country_id: int,
) -> CountryResponse:
    """
    Retrieve a country by its ID.

    Args:
        session (SessionDep): The database session.
        country_id (int): The ID of the country to retrieve.

    Returns:
        CountryResponse: The retrieved country.
    """
    return await get_country_by_id(session=session, country_id=country_id)


@router.get("/kitchens/{kitchen_id}/", response_model=KitchenResponse)
async def get_kitchen(
    session: SessionDep,
    kitchen_id: int,
) -> KitchenResponse:
    """
    Retrieve a kitchen by its ID.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to retrieve.

    Returns:
        KitchenResponse: The retrieved kitchen.
    """
    return await get_kitchen_by_id(session=session, kitchen_id=kitchen_id)


@router.put("/countries/{country_id}/", response_model=CountryResponse)
async def put_country(
    session: SessionDep,
    country_id: int,
    country: CountryUpdate,
    _: None = Depends(is_admin),
) -> CountryResponse:
    """
    Update an existing country in the database.

    Args:
        session (SessionDep): The database session.
        country_id (int): The ID of the country to update.
        country (CountryUpdate): The country details to update.

    Returns:
        CountryResponse: The updated country.
    """
    return await update_country(
        session=session, country_id=country_id, country_update=country
    )


@router.put("/kitchens/{kitchen_id}/", response_model=KitchenResponse)
async def put_kitchen(
    session: SessionDep,
    kitchen_id: int,
    kitchen: KitchenUpdate,
    _: None = Depends(is_admin),
) -> KitchenResponse:
    """
    Update an existing kitchen in the database.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to update.
        kitchen (KitchenUpdate): The kitchen details to update.

    Returns:
        KitchenResponse: The updated kitchen.
    """
    return await update_kitchen(
        session=session, kitchen_id=kitchen_id, kitchen_update=kitchen
    )


@router.delete("/countries/{country_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
    session: SessionDep,
    country_id: int,
    _: None = Depends(is_admin),
) -> None:
    """
    Delete an existing country from the database.

    Args:
        session (SessionDep): The database session.
        country_id (int): The ID of the country to delete.
    """
    await remove_country(session=session, country_id=country_id)


@router.delete("/kitchens/{kitchen_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kitchen(
    session: SessionDep,
    kitchen_id: int,
    _: None = Depends(is_admin),
) -> None:
    """
    Delete an existing kitchen from the database.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to delete.
    """
    await remove_kitchen(session=session, kitchen_id=kitchen_id)
