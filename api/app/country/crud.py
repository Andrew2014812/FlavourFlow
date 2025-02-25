from typing import List

from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.country.models import Country
from api.app.country.schemas import CountryResponse, CountryCreate, CountryUpdate


async def create_country(session: SessionDep, country_create: CountryCreate) -> CountryResponse:
    statement = select(Country).filter(
        Country.title_ua == country_create.title_ua,
        Country.title_en == country_create.title_en,
    )
    result = await session.exec(statement)
    existing_country: Country = result.first()

    if existing_country:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country already exists")

    db_country = Country()

    for key, value in country_create.model_dump().items():
        setattr(db_country, key, value)

    session.add(db_country)
    await session.commit()
    await session.refresh(db_country)

    return db_country


async def get_all_countries(session: SessionDep) -> List[CountryResponse]:
    result = await session.exec(select(Country))
    return result.all()


async def get_country_by_id(session: SessionDep, country_id: int) -> CountryResponse:
    statement = select(Country).filter(Country.id == country_id)
    result = await session.exec(statement)
    existing_country: Country = result.first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    return existing_country


async def update_country(session: SessionDep, country_id: int, country_update: CountryUpdate) -> CountryResponse:
    statement = select(Country).filter(Country.id == country_id)
    result = await session.exec(statement)
    existing_country: Country = result.first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    for key, value in country_update.model_dump().items():
        setattr(existing_country, key, value)

    await session.merge(existing_country)
    await session.commit()
    await session.refresh(existing_country)

    return existing_country


async def remove_country(session: SessionDep, country_id: int):
    statement = select(Country).filter(Country.id == country_id)
    result = await session.exec(statement)
    existing_country: Country = result.first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    await session.delete(existing_country)
    await session.commit()
