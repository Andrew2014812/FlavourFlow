from typing import List

from fastapi import APIRouter

from api.app.common.dependencies import SessionDep
from api.app.country.crud import get_all_countries, create_country
from api.app.country.schemas import CountryResponse, CountryCreate

router = APIRouter()


@router.get("/")
def get_countries(session: SessionDep) -> List[CountryResponse]:
    return get_all_countries(session)


@router.post("/")
def post_country(session: SessionDep, country: CountryCreate) -> CountryResponse:
    return create_country(session, country)
