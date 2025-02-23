from enum import Enum

company_prefix = 'company'

class CompanyEndpoints(Enum):
    COMPANY_GET = "users/me/"
    COMPANY_UPDATE = "users/update/me/"
    COMPANY_CREATE = "users/register/"
    COMPANY_DELETE = "users/token/"


async def get_user(telegram_id: int) -> UserResponseMe | None:
    user_info = get_user_info(telegram_id)

    if not user_info or not user_info.is_registered:
        return None

    response = await make_request(
        sub_url=CompanyEndpoints.COMPANY_GET.value,
        method=APIMethods.GET.value,
        headers={APIAuth.AUTH.value: f'{user_info.token_type} {user_info.access_token}'},
    )

    return UserResponseMe.model_validate(response.get('data'))