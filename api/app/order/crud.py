from api.app.utils import get_entity_by_params

from ..common.dependencies import SessionDep
from .models import Order, OrderItem
from .schemas import OrderCreate


async def create_order(
    session: SessionDep,
    user_id: int,
    order_create: OrderCreate,
) -> Order:
    order = Order(user_id=user_id, total_price=order_create.total_price)

    session.add(order)
    await session.flush()

    for item in order_create.order_items:
        order_item = OrderItem(
            **item.model_dump(),
            order_id=order.id,
        )
        session.add(order_item)

    await session.commit()
    await session.refresh(order)

    return await get_entity_by_params(
        session,
        Order,
        id=order.id,
        user_id=user_id,
    )
