from enum import Enum
from typing import Dict

from api.app.company.schemas import CompanyResponse
from bot.common.services.bot.user_info_service import get_user_info
from bot.common.utils import make_request
from bot.config import APIMethods, APIAuth

company_prefix = 'company'


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
        headers={APIAuth.AUTH.value: f'{user_info.token_type} {user_info.access_token}'},
        body=body,
    )

    return CompanyResponse.model_validate(response.get('data'))
