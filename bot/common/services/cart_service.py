from ...common.utils import make_request
from ...config import APIAuth, APIMethods
from .user_info_service import get_user_info

BASE = "cart"


async def add_to_cart(telegram_id: int, product_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    data = {"product_id": product_id, "quantity": 1}
    response = await make_request(
        sub_url=f"{BASE}/add/",
        method=APIMethods.POST.value,
        body=data,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response
