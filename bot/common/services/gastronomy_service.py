import logging
from enum import Enum
from typing import Dict, Optional

from api.app.gastronomy.schemas import (
    CountryListResponse,
    CountryResponse,
    KitchenListResponse,
    KitchenResponse,
)

from ...common.services.user_info_service import get_user_info
from ...config import APIAuth, APIMethods
from ..utils import make_request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityType(Enum):
    COUNTRY = "country"
    KITCHEN = "kitchen"


class GastronomyService:
    def __init__(self, entity_type: EntityType, list_schema, item_schema):
        self.prefix = f"gastronomy/{entity_type.value}s/"
        self.list_schema = list_schema
        self.item_schema = item_schema

    async def get_list(self, page: int = 1) -> Optional[Dict]:
        try:
            response = await make_request(
                sub_url=self.prefix,
                method=APIMethods.GET.value,
                params={"page": page},
            )
            return self.list_schema.model_validate(response.get("data"))

        except Exception as e:
            error_msg = getattr(e, "detail", str(e))
            status_code = getattr(e, "status_code", None) or 500
            logger.error(
                f"Error fetching list for {self.prefix}: {error_msg} (Status: {status_code})"
            )

            return {"error": error_msg, "status": "failed", "status_code": status_code}

    async def get_item(self, item_id: int) -> Optional[Dict]:
        try:
            response = await make_request(
                sub_url=f"{self.prefix}{item_id}/",
                method=APIMethods.GET.value,
            )
            return self.item_schema.model_validate(response.get("data"))

        except Exception as e:
            error_msg = getattr(e, "detail", str(e))
            status_code = getattr(e, "status_code", None) or 500
            logger.error(
                f"Error fetching item {item_id} for {self.prefix}: {error_msg} (Status: {status_code})"
            )
            return {"error": error_msg, "status": "failed", "status_code": status_code}

    async def create(self, data: Dict, telegram_id: int) -> Optional[Dict]:
        try:
            user_info = await get_user_info(telegram_id)
            response = await make_request(
                sub_url=self.prefix,
                method=APIMethods.POST.value,
                body=data,
                headers={
                    APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
                },
            )
            return self.item_schema.model_validate(response.get("data"))
        except Exception as e:
            error_msg = getattr(e, "detail", str(e))
            status_code = getattr(e, "status_code", None) or 500
            logger.error(
                f"Error creating item for {self.prefix}: {error_msg} (Status: {status_code})"
            )
            return {"error": error_msg, "status": "failed", "status_code": status_code}

    async def update(
        self, item_id: int, data: Dict, telegram_id: int
    ) -> Optional[Dict]:
        try:
            user_info = await get_user_info(telegram_id)
            response = await make_request(
                sub_url=f"{self.prefix}{item_id}/",
                method=APIMethods.PATCH.value,
                body=data,
                headers={
                    APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
                },
            )
            return self.item_schema.model_validate(response.get("data"))
        except Exception as e:
            error_msg = getattr(e, "detail", str(e))
            status_code = getattr(e, "status_code", None) or 500
            logger.error(
                f"Error updating item {item_id} for {self.prefix}: {error_msg} (Status: {status_code})"
            )
            return {"error": error_msg, "status": "failed", "status_code": status_code}

    async def delete(self, item_id: int, telegram_id: int) -> Optional[Dict]:
        try:
            user_info = await get_user_info(telegram_id)
            await make_request(
                sub_url=f"{self.prefix}{item_id}/",
                method=APIMethods.DELETE.value,
                headers={
                    APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
                },
            )
            return {"status": "success"}
        except Exception as e:
            error_msg = getattr(e, "detail", str(e))
            status_code = getattr(e, "status_code", None) or 500
            logger.error(
                f"Error deleting item {item_id} for {self.prefix}: {error_msg} (Status: {status_code})"
            )
            return {"error": error_msg, "status": "failed", "status_code": status_code}


country_service = GastronomyService(
    EntityType.COUNTRY, CountryListResponse, CountryResponse
)
kitchen_service = GastronomyService(
    EntityType.KITCHEN, KitchenListResponse, KitchenResponse
)
