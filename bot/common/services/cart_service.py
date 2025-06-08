from typing import List

from api.app.cart.schemas import CartItemFullResponse, CartItemResponse

from ...common.utils import make_request
from ...config import APIAuth, APIMethods
from .user_info_service import get_user_info

BASE = "cart"


async def add_to_cart(telegram_id: int, product_id: int, company_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    data = {"product_id": product_id, "quantity": 1, "company_id": company_id}
    response = await make_request(
        sub_url=f"{BASE}/add/",
        method=APIMethods.POST.value,
        body=data,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response


async def clear_cart(telegram_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/clear/",
        method=APIMethods.DELETE.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response


async def get_cart_items(
    telegram_id: int, page: int = None, return_all: bool = False
) -> CartItemFullResponse | List[CartItemResponse] | None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/",
        method=APIMethods.GET.value,
        params={"page": page} if page else {"return_all": str(return_all)},
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    if response.get("data") is None:
        return None

    if return_all:
        return [CartItemResponse(**item) for item in response.get("data")]

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


async def remove_from_cart(telegram_id: int, item_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/remove/{item_id}/",
        method=APIMethods.DELETE.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response
