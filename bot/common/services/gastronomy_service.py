from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar

from api.app.gastronomy.schemas import (
    CountryListResponse,
    CountryResponse,
    KitchenListResponse,
    KitchenResponse,
)
from bot.common.services.user_info_service import get_user_info

from ...config import APIAuth, APIMethods
from ..utils import make_request

T = TypeVar("T")


class EntityType(Enum):
    COUNTRY = "country"
    KITCHEN = "kitchen"


class GastronomyService(Generic[T]):
    def __init__(self, entity_type: EntityType, list_schema: type, item_schema: type):
        self.prefix = f"gastronomy/{entity_type.value}s"
        self.list_schema = list_schema
        self.item_schema = item_schema

    async def get_list(self, page: int = 1) -> Optional[T]:
        response = await make_request(
            sub_url=f"{self.prefix}/",
            method=APIMethods.GET.value,
            params={"page": page},
        )
        return self.list_schema.model_validate(response.get("data"))

    async def get_item(self, item_id: int) -> Optional[T]:
        response = await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.GET.value,
        )
        return self.item_schema.model_validate(response.get("data"))

    async def create(self, body: Dict[str, Any], telegram_id: int) -> Optional[T]:
        user_info = await get_user_info(telegram_id)
        response = await make_request(
            sub_url=f"{self.prefix}/",
            method=APIMethods.POST.value,
            body=body,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return self.item_schema.model_validate(response.get("data"))

    async def update(
        self, item_id: int, body: Dict[str, Any], telegram_id: int
    ) -> Optional[T]:
        user_info = await get_user_info(telegram_id)
        response = await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.PATCH.value,
            body=body,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return self.item_schema.model_validate(response.get("data"))

    async def delete(self, item_id: int, telegram_id: int) -> None:
        user_info = await get_user_info(telegram_id)
        await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.DELETE.value,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )


country_service = GastronomyService(
    EntityType.COUNTRY,
    CountryListResponse,
    CountryResponse,
)

kitchen_service = GastronomyService(
    EntityType.KITCHEN,
    KitchenListResponse,
    KitchenResponse,
)
