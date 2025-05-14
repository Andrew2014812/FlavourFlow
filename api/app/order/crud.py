from ..cart.models import Cart
from ..common.dependencies import SessionDep
from ..utils import get_entity_by_params
from .models import Order, OrderItem
from .schemas import OrderCreate


async def create_order(
    session: SessionDep,
    user_id: int,
    order_create: OrderCreate,
) -> Order:
    order = Order(
        user_id=user_id,
        total_price=order_create.total_price,
        address=order_create.address,
        time=order_create.time,
    )

    session.add(order)
    await session.flush()

    for item in order_create.order_items:
        order_item = OrderItem(
            **item.model_dump(),
            order_id=order.id,
        )
        session.add(order_item)

    cart = await get_entity_by_params(session, Cart, user_id=user_id)

    await session.delete(cart)
    await session.commit()
    await session.refresh(order)

    return await get_entity_by_params(
        session,
        Order,
        id=order.id,
        user_id=user_id,
    )
