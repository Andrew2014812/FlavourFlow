from enum import Enum
from typing import Dict, List, Optional

from api.app.company.schemas import CompanyListResponse, CompanyResponse

from ...common.services.user_info_service import get_user_info
from ...config import APIAuth, APIMethods
from ..utils import make_request

company_prefix = "company"


class CompanyEndpoints(Enum):
    COMPANY_GET = f"{company_prefix}/"
    COMPANY_UPDATE = f"{company_prefix}/"
    COMPANY_CREATE = f"{company_prefix}/"
    COMPANY_DELETE = f"{company_prefix}/"


async def create_company(telegram_id: int, body: Dict) -> CompanyResponse | None:
    user_info = get_user_info(telegram_id)

    response = await make_request(
        sub_url=CompanyEndpoints.COMPANY_CREATE.value,
        method=APIMethods.POST.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
        body=body,
    )

    return CompanyResponse.model_validate(response.get("data"))


class CompanyService:
    def __init__(self, list_schema: type, item_schema: type):
        self.prefix = "company"
        self.list_schema = list_schema
        self.item_schema = item_schema

    async def get_list(self, page: int = 1) -> Optional[List[CompanyResponse]]:
        response = await make_request(
            sub_url=f"{self.prefix}/",
            method=APIMethods.GET.value,
            params={"page": page},
        )
        return CompanyListResponse.model_validate(response.get("data"))

    async def get_item(self, item_id: int) -> Optional[CompanyResponse]:
        response = await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.GET.value,
        )
        return CompanyResponse.model_validate(response.get("data"))

    async def create(self, body: Dict, telegram_id: int) -> Optional[CompanyResponse]:
        user_info = await get_user_info(telegram_id)

        response = await make_request(
            sub_url=f"{self.prefix}/",
            method=APIMethods.POST.value,
            body=body,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return CompanyResponse.model_validate(response.get("data"))

    async def update(
        self, item_id: int, body: Dict, telegram_id: int
    ) -> Optional[CompanyResponse]:
        user_info = await get_user_info(telegram_id)

        response = await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.PATCH.value,
            body=body,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )

        return CompanyResponse.model_validate(response.get("data"))

    async def delete(self, item_id: int, telegram_id: int) -> None:
        user_info = await get_user_info(telegram_id)

        await make_request(
            sub_url=f"{self.prefix}/{item_id}/",
            method=APIMethods.DELETE.value,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )


company_service = CompanyService(CompanyListResponse, CompanyResponse)
