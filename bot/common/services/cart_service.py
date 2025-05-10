from api.app.cart.schemas import CartItemFullResponse

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


async def get_cart_items(telegram_id: int, page: int) -> CartItemFullResponse | None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/",
        method=APIMethods.GET.value,
        params={"page": page},
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return CartItemFullResponse.model_validate(response.get("data"))


async def change_amount(telegram_id: int, item_id: int, amount: int) -> None:
    user_info = await get_user_info(telegram_id)
    data = {"item_id": item_id, "amount": amount}
    response = await make_request(
        sub_url=f"{BASE}/amount/",
        method=APIMethods.PATCH.value,
        body=data,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response
