from enum import Enum
from typing import Optional

from api.app.gastronomy.schemas import (
    CountryListResponse,
    CountryResponse,
    KitchenListResponse,
    KitchenResponse,
)
from bot.common.services.user_info_service import get_user_info

from ...config import APIAuth, APIMethods
from ..utils import make_request

country_prefix = "gastronomy/countries"
kitchen_prefix = "gastronomy/kitchens"


class GastronomyEndpoints(Enum):
    COUNTRY_GET = f"{country_prefix}/"
    COUNTRY_UPDATE = f"{country_prefix}/"
    COUNTRY_CREATE = f"{country_prefix}/"
    COUNTRY_DELETE = f"{country_prefix}/"

    KITCHEN_GET = f"{kitchen_prefix}/"
    KITCHEN_UPDATE = f"{kitchen_prefix}/"
    KITCHEN_CREATE = f"{kitchen_prefix}/"
    KITCHEN_DELETE = f"{kitchen_prefix}/"


async def get_country_list(page: int = 1) -> Optional[CountryListResponse]:

    response = await make_request(
        sub_url=GastronomyEndpoints.COUNTRY_GET.value,
        method=APIMethods.GET.value,
        params={"page": page},
    )

    return CountryListResponse.model_validate(response.get("data"))


async def get_kitchen_list(page: int = 1) -> Optional[KitchenListResponse]:

    response = await make_request(
        sub_url=GastronomyEndpoints.KITCHEN_GET.value,
        method=APIMethods.GET.value,
        params={"page": page},
    )

    return KitchenListResponse.model_validate(response.get("data"))


async def get_country(country_id: int) -> Optional[CountryResponse]:
    url = f"{GastronomyEndpoints.COUNTRY_GET.value}{country_id}/"

    response = await make_request(
        sub_url=url,
        method=APIMethods.GET.value,
    )

    return CountryResponse.model_validate(response.get("data"))


async def get_kitchen(kitchen_id: int) -> Optional[KitchenResponse]:
    url = f"{GastronomyEndpoints.KITCHEN_GET.value}{kitchen_id}/"

    response = await make_request(
        sub_url=url,
        method=APIMethods.GET.value,
    )

    return KitchenResponse.model_validate(response.get("data"))


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


async def create_kitchen(body: dict, telegram_id: int) -> Optional[KitchenResponse]:
    user_info = await get_user_info(telegram_id)

    response = await make_request(
        sub_url=GastronomyEndpoints.KITCHEN_CREATE.value,
        method=APIMethods.POST.value,
        body=body,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return KitchenResponse.model_validate(response.get("data"))


async def update_country(
    country_id: int,
    body: dict,
    telegram_id: int,
) -> Optional[CountryResponse]:
    user_info = await get_user_info(telegram_id)

    response = await make_request(
        sub_url=f"{GastronomyEndpoints.COUNTRY_UPDATE.value}{country_id}/",
        method=APIMethods.PATCH.value,
        body=body,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return CountryResponse.model_validate(response.get("data"))


async def update_kitchen(
    kitchen_id: int,
    body: dict,
    telegram_id: int,
) -> Optional[KitchenResponse]:
    user_info = await get_user_info(telegram_id)

    response = await make_request(
        sub_url=f"{GastronomyEndpoints.KITCHEN_UPDATE.value}{kitchen_id}/",
        method=APIMethods.PATCH.value,
        body=body,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return KitchenResponse.model_validate(response.get("data"))


async def delete_country(country_id: int, telegram_id: int):
    user_info = await get_user_info(telegram_id)

    await make_request(
        sub_url=f"{GastronomyEndpoints.COUNTRY_DELETE.value}{country_id}/",
        method=APIMethods.DELETE.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )


async def delete_kitchen(kitchen_id: int, telegram_id: int):
    user_info = await get_user_info(telegram_id)

    await make_request(
        sub_url=f"{GastronomyEndpoints.KITCHEN_DELETE.value}{kitchen_id}/",
        method=APIMethods.DELETE.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )
