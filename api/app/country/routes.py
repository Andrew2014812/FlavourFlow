from typing import List

from fastapi import APIRouter, Depends

from api.app.common.dependencies import SessionDep
from api.app.country.crud import (
    get_all_countries,
    create_country,
    update_country,
    remove_country,
    get_country_by_id,
)
from api.app.country.schemas import CountryResponse, CountryCreate, CountryUpdate
from api.app.user.crud import is_admin

router = APIRouter()


@router.get("/")
def get_countries(session: SessionDep) -> List[CountryResponse]:
    """
    Retrieve a list of all countries.

    Args:
        session (SessionDep): The database session.

    Returns:
        List[CountryResponse]: A list of country details.
    """

    return get_all_countries(session)


@router.post("/")
def post_country(
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

    return create_country(session, country)


@router.get("/{country_id}/")
def kitchen_get(
        session: SessionDep, country_id: int) -> CountryResponse:
    """
    Retrieve a country by id.

    Args:
        session (SessionDep): The database session.
        country_id (int): The id of the country to retrieve

    Returns:
        CountryResponse: The retrieved country
    """

    return get_country_by_id(session, country_id)


@router.put("/{country_id}/")
def put_country(
        session: SessionDep,
        country_id: int,
        country: CountryUpdate,
        _: None = Depends(is_admin),
) -> CountryResponse:
    """
    Update an existing country in the database.

    Args:
        session (SessionDep): The database session.
        country_id (int): The id of the country to update.
        country (CountryUpdate): The country details to update.

    Returns:
        CountryResponse: The updated country.
    """

    return update_country(session=session, country_id=country_id, country=country)


@router.delete("/{country_id}/")
def delete_country(
        session: SessionDep,
        country_id: int,
        _: None = Depends(is_admin),
) -> dict:
    """
    Delete an existing country in the database.

    Args:
        session (SessionDep): The database session.
        country_id (int): The id of the country to delete.

    Returns:
        dict: A message indicating success or failure of the deletion.
    """

    return remove_country(session=session, country_id=country_id)
