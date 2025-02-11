from typing import List

from fastapi import APIRouter, Depends

from api.app.common.dependencies import SessionDep
from api.app.kitchen.crud import (
    get_kitchen_list,
    create_kitchen,
    update_kitchen,
    remove_kitchen,
    get_kitchen_by_id,
)
from api.app.kitchen.schemas import KitchenResponse, KitchenCreate, KitchenUpdate
from api.app.user.crud import is_admin

router = APIRouter()


@router.get("/")
def kitchen_list(session: SessionDep) -> List[KitchenResponse]:
    """
    Retrieve a list of all kitchens.

    Args:
        session (SessionDep): The database session.

    Returns:
        List[KitchenResponse]: A list of kitchen details.
    """

    return get_kitchen_list(session=session)


@router.get("/{kitchen_id}/")
def kitchen_get(session: SessionDep, kitchen_id: int) -> KitchenResponse:
    """
    Get a kitchen by its ID.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to retrieve.

    Returns:
        KitchenResponse: The retrieved kitchen.
    """

    return get_kitchen_by_id(session=session, kitchen_id=kitchen_id)


@router.post("/")
def post_country(
        session: SessionDep,
        kitchen: KitchenCreate,
        _: None = Depends(is_admin),
) -> KitchenResponse:
    """
    Create a new kitchen in the database.

    Args:
        session (SessionDep): The database session.
        kitchen (KitchenCreate): The kitchen to be created.

    Returns:
        KitchenResponse: The created kitchen.
    """

    return create_kitchen(session=session, kitchen=kitchen)


@router.put("/{kitchen_id}/")
def put_country(
        session: SessionDep,
        kitchen_id: int,
        kitchen: KitchenUpdate,
        _: None = Depends(is_admin),
) -> KitchenResponse:
    """
    Update an existing kitchen in the database.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to update.
        kitchen (KitchenUpdate): The kitchen details to update.

    Returns:
        KitchenResponse: The updated kitchen.
    """

    return update_kitchen(session=session, kitchen_id=kitchen_id, kitchen=kitchen)


@router.delete("/{kitchen_id}/")
def delete_country(
        session: SessionDep,
        kitchen_id: int,
        _: None = Depends(is_admin),
) -> dict:
    """
    Delete an existing kitchen from the database.

    Args:
        session (SessionDep): The database session.
        kitchen_id (int): The ID of the kitchen to delete.

    Returns:
        dict: A message indicating the success or failure of the deletion.
    """

    return remove_kitchen(session=session, kitchen_id=kitchen_id)
