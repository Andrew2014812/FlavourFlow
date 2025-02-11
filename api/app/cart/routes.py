from typing import List

from fastapi import APIRouter, Depends, status

from api.app.cart.crud import add_to_cart, get_cart_items, remove_cart_item
from api.app.cart.schemas import CartItemCreate, CartItemResponse
from api.app.common.dependencies import SessionDep
from api.app.user.crud import get_current_user
from api.app.user.models import User

router = APIRouter()


@router.get("/")
def get_cart(
        session: SessionDep,
        current_user: User = Depends(get_current_user),
) -> List[CartItemResponse]:
    """
    Retrieve the items in the user's cart.

    Args:
        session (SessionDep): The database session.
        current_user (User, optional): The user to retrieve the cart for. Defaults to the current user.

    Returns:
        List[CartItemResponse]: The items in the cart.
    """

    return get_cart_items(session=session, user_id=current_user.id)


@router.post("/add/")
def post_cart_item(
        new_item: CartItemCreate,
        session: SessionDep,
        current_user: User = Depends(get_current_user),
) -> CartItemResponse:
    """
    Add a new item to the user's cart.

    Args:
        new_item (CartItemCreate): The item to add.
        session (SessionDep): The database session.
        current_user (User, optional): The user to add the item for. Defaults to the current user.

    Returns:
        CartItemResponse: The added item.
    """

    return add_to_cart(session=session, user_id=current_user.id, new_item=new_item)


@router.delete("/remove/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
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

    remove_cart_item(session=session, user_id=current_user.id, item_id=item_id)
