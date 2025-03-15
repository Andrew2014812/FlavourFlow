from enum import Enum
from typing import Optional

from api.app.gastronomy.schemas import CountryListResponse, CountryResponse
from bot.common.services.user_info_service import get_user_info

from ...config import APIAuth, APIMethods
from ..utils import make_request

country_prefix = "gastronomy/countries"


class GastronomyEndpoints(Enum):
    COUNTRY_GET_LIST = f"{country_prefix}/"
    COUNTRY_UPDATE = f"{country_prefix}/"
    COUNTRY_CREATE = f"{country_prefix}/"
    COUNTRY_DELETE = f"{country_prefix}/"


async def get_country_list(page: int = 1) -> Optional[CountryListResponse]:

    response = await make_request(
        sub_url=GastronomyEndpoints.COUNTRY_GET_LIST.value,
        method=APIMethods.GET.value,
        params={"page": page},
    )

    return CountryListResponse.model_validate(response.get("data"))


async def create_country(body: dict, telegram_id: int) -> Optional[CountryResponse]:
    user_info = await get_user_info(telegram_id)

    response = await make_request(
        sub_url=GastronomyEndpoints.COUNTRY_CREATE.value,
        method=APIMethods.POST.value,
        body=body,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return CountryResponse.model_validate(response.get("data"))
