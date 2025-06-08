from typing import List

from api.app.wishlist.schemas import WishlistItemFullResponse, WishlistItemResponse

from ...common.utils import make_request
from ...config import APIAuth, APIMethods
from .user_info_service import get_user_info

BASE = "wishlist"


async def add_to_wishlist(telegram_id: int, product_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/add/{product_id}/",
        method=APIMethods.POST.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response


async def get_wishlist_items(
    telegram_id: int, page: int = None, return_all: bool = False
) -> WishlistItemFullResponse | List[WishlistItemResponse] | None:
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
        return [WishlistItemResponse(**item) for item in response.get("data")]

    return WishlistItemFullResponse.model_validate(response.get("data"))


async def remove_from_wishlist(telegram_id: int, item_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/remove/{item_id}/",
        method=APIMethods.DELETE.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response


async def move_to_cart(telegram_id: int, item_id: int) -> None:
    user_info = await get_user_info(telegram_id)
    response = await make_request(
        sub_url=f"{BASE}/move/{item_id}/",
        method=APIMethods.PUT.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return response
