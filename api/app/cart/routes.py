from typing import List

from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..user.crud import get_current_user
from ..user.models import User
from .crud import add_to_cart, get_cart_items, remove_cart_item
from .schemas import CartItemCreate, CartItemResponse

router = APIRouter()


@router.get("/")
async def get_cart(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> List[CartItemResponse]:

    return await get_cart_items(session=session, user_id=current_user.id)


@router.post("/add/")
async def post_cart_item(
    new_item: CartItemCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> CartItemResponse:

    return await add_to_cart(
        session=session, user_id=current_user.id, new_item=new_item
    )


@router.delete("/remove/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    session: SessionDep,
    item_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Remove an item from the user's cart.

    Args:
        session (SessionDep): The database session.
        item_id (int): The ID of the item to remove.
        current_user (User, optional): The user to remove the item for. Defaults to the current user.

    Returns:
        dict: A message indicating the success of the removal.
    """

    await remove_cart_item(session=session, user_id=current_user.id, item_id=item_id)
