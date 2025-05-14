from fastapi import APIRouter, Depends

from ..common.dependencies import SessionDep
from ..user.crud import get_current_user
from ..user.models import User
from .crud import create_order
from .models import Order
from .schemas import OrderCreate

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
