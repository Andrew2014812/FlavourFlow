from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload

from ..common.dependencies import SessionDep
from ..user.crud import get_current_user, is_admin
from ..user.models import User
from ..utils import get_entity_by_params
from .crud import create_order
from .models import Order, OrderItem
from .schemas import OrderCreate, OrderResponse

router = APIRouter()


@router.post("/")
async def post_order(
    session: SessionDep,
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
) -> Order:
    return await create_order(
        session=session,
        order_create=order,
        user_id=current_user.id,
    )


@router.put("/pay/{order_id}/")
async def update_order_purchase_info(
    session: SessionDep,
    order_id: int,
    _: User = Depends(get_current_user),
) -> None:
    order: Order = await get_entity_by_params(
        session,
        Order,
        id=order_id,
    )

    order.is_payed = True
    await session.commit()


@router.put("/accept/{order_id}/")
async def accept_order(
    session: SessionDep,
    order_id: int,
    _: User = Depends(is_admin),
) -> None:
    order: Order = await get_entity_by_params(
        session,
        Order,
        id=order_id,
    )

    if order.is_submitted:
        raise HTTPException(
            status_code=400,
            detail="Order is already submitted",
        )

    order.is_submitted = True
    await session.commit()


@router.get("/id/{order_id}/")
async def get_order(
    session: SessionDep,
    order_id: int,
    _: User = Depends(get_current_user),
) -> OrderResponse:
    return await get_entity_by_params(
        session,
        Order,
        id=order_id,
        options=[
            joinedload(Order.order_items).joinedload(OrderItem.product),
            joinedload(Order.user),
            joinedload(Order.company),
        ],
    )


@router.get("/")
async def get_paid_orders(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> List[OrderResponse]:
    return await get_entity_by_params(
        session,
        Order,
        user_id=current_user.id,
        is_payed=True,
        return_all=True,
        options=[
            joinedload(Order.order_items).joinedload(OrderItem.product),
            joinedload(Order.user),
            joinedload(Order.company),
        ],
    )


@router.get("/admin/")
async def get_all_orders(
    session: SessionDep,
    _: User = Depends(is_admin),
) -> List[OrderResponse]:
    return await get_entity_by_params(
        session,
        Order,
        return_all=True,
        options=[
            joinedload(Order.order_items).joinedload(OrderItem.product),
            joinedload(Order.user),
            joinedload(Order.company),
        ],
    )
