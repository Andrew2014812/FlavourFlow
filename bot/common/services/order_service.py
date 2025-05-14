from api.app.order.models import Order
from api.app.order.schemas import OrderCreate, OrderResponse
from bot.config import APIAuth, APIMethods

from ...common.services.user_info_service import get_user_info
from ...common.utils import make_request

BASE = "order"


async def create_order(order_create: OrderCreate, user_id: int):
    user_info = await get_user_info(user_id)
    response = await make_request(
        sub_url=f"{BASE}/",
        method=APIMethods.POST.value,
        body=order_create.model_dump(),
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return Order.model_validate(response.get("data"))


async def update_order_purchase_info(order_id: int, user_id: int):
    user_info = await get_user_info(user_id)
    await make_request(
        sub_url=f"{BASE}/{order_id}/",
        method=APIMethods.PUT.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )


async def get_paid_orders(user_id: int):
    user_info = await get_user_info(user_id)
    response = await make_request(
        sub_url=f"{BASE}/",
        method=APIMethods.GET.value,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )

    return [OrderResponse.model_validate(item) for item in response.get("data")]
