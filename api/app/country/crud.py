from typing import List

from fastapi import HTTPException, status

from api.app.common.dependencies import SessionDep
from api.app.country.models import Country
from api.app.country.schemas import CountryResponse, CountryCreate, CountryUpdate


def create_country(session: SessionDep, country: CountryCreate) -> CountryResponse:
    existing_country: Country = session.query(Country).filter(Country.title == country.title).first()

    if existing_country:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country already exists")

    db_country = Country(title=country.title)

    session.add(db_country)
    session.commit()
    session.refresh(db_country)

    return db_country


def get_all_countries(session: SessionDep) -> List[CountryResponse]:
    countries: List[CountryResponse] = session.query(Country).all()
    return countries


def get_country_by_id(session: SessionDep, country_id: int) -> CountryResponse:
    existing_country: Country = session.query(Country).filter(Country.id == country_id).first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    return existing_country


def update_country(session: SessionDep, country_id: int, country: CountryUpdate) -> CountryResponse:
    existing_country = session.query(Country).filter(Country.id == country_id).first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    existing_country.title = country.title

    session.merge(existing_country)
    session.commit()
    session.refresh(existing_country)

    return existing_country


def remove_country(session: SessionDep, country_id: int) -> dict:
    existing_country: Country = session.query(Country).filter(Country.id == country_id).first()

    if not existing_country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

    session.delete(existing_country)
    session.commit()

    return {"message": "Country deleted successfully", "country_id": country_id}
