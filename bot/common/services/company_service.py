from enum import Enum
from typing import Dict, List, Optional

from api.app.company.schemas import CompanyListResponse, CompanyResponse

from ...common.services.user_info_service import get_user_info
from ...config import APIAuth, APIMethods
from ..utils import make_request
from .gastronomy_service import kitchen_service


class CompanyEndpoints(Enum):
    BASE = "company/"


async def create_company(telegram_id: int, data: Dict) -> Optional[CompanyResponse]:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=CompanyEndpoints.BASE.value,
        method=APIMethods.POST.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
        body=data,
    )
    return CompanyResponse.model_validate(response.get("data"))


class CompanyService:
    def __init__(self):
        self.prefix = "company/"

    async def get_categories(self, language_code: str) -> List[Dict]:
        kitchens = await kitchen_service.get_list()
        return [
            {"text": kitchen.title_ua if language_code == "ua" else kitchen.title_en}
            for kitchen in kitchens
        ]

    async def get_list(
        self, page: int = 1, limit: int = 6
    ) -> Optional[CompanyListResponse]:
        response = await make_request(
            sub_url=self.prefix,
            method=APIMethods.GET.value,
            params={"page": page, "limit": limit},
        )
        return CompanyListResponse.model_validate(response.get("data"))

    async def get_item(self, item_id: int) -> Optional[CompanyResponse]:
        response = await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.GET.value,
        )
        return CompanyResponse.model_validate(response.get("data"))

    async def create(self, data: Dict, telegram_id: int) -> Optional[CompanyResponse]:
        user_info = await get_user_info(telegram_id)
        response = await make_request(
            sub_url=self.prefix,
            method=APIMethods.POST.value,
            body=data,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return CompanyResponse.model_validate(response.get("data"))

    async def update(
        self, item_id: int, data: Dict, telegram_id: int
    ) -> Optional[CompanyResponse]:
        user_info = await get_user_info(telegram_id)
        response = await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.PATCH.value,
            body=data,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return CompanyResponse.model_validate(response.get("data"))

    async def delete(self, item_id: int, telegram_id: int) -> None:
        user_info = await get_user_info(telegram_id)
        await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.DELETE.value,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )


company_service = CompanyService()
