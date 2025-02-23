from typing import List

from fastapi import APIRouter, Depends, status

from api.app.common.dependencies import SessionDep
from api.app.product.crud import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    remove_product,
)
from api.app.product.schemas import ProductCreate, ProductResponse, ProductPatch
from api.app.user.crud import is_admin

router = APIRouter()


@router.get("/")
def product_list(
        session: SessionDep, page: int = 1, limit: int = 10
) -> List[ProductResponse]:
    """
    Retrieve a list of all products.

    Args:
        session (SessionDep): The database session.
        page (int, optional): The page number. Defaults to 1.
        limit (int, optional): The page size. Defaults to 10.

    Returns:
        List[ProductResponse]: A list of product details.
    """

    return get_all_products(session=session, page=page, limit=limit)


@router.get("/{product_id}/")
def company_detail(product_id: int, session: SessionDep) -> ProductResponse:
    """
    Retrieve a product by its ID.

    Args:
        product_id (int): The ID of the product to retrieve.
        session (SessionDep): The database session.

    Returns:
        ProductResponse: The retrieved product.
    """

    return get_product_by_id(session=session, product_id=product_id)


@router.post("/")
async def post_product(
        session: SessionDep, product: ProductCreate = Depends(ProductCreate.as_form),
        _: None = Depends(is_admin),
) -> ProductResponse:
    """
    Create a new product in the database.

    Args:
        session (SessionDep): The database session.
        product (ProductCreate): The product to be created.

    Returns:
        ProductResponse: The created product.
    """

    return await create_product(session=session, product_create=product)


@router.put("/{product_id}/")
async def put_company(
        product_id: int,
        session: SessionDep,
        product: ProductCreate = Depends(ProductCreate.as_form),
        _: None = Depends(is_admin),
) -> ProductResponse:
    """
    Update a product in the database.

    Args:
        product_id (int): The ID of the product to update.
        session (SessionDep): The database session.
        product (ProductCreate): The product to be updated.

    Returns:
        ProductResponse: The updated product.
    """

    return await update_product(session=session, product=product, product_id=product_id)


@router.patch("/{product_id}/")
async def patch_company(
        product_id: int,
        session: SessionDep,
        product: ProductPatch = Depends(ProductPatch.as_form),
        _: None = Depends(is_admin),
) -> ProductResponse:
    """
    Patch a product in the database.

    Args:
        product_id (int): The ID of the product to patch.
        session (SessionDep): The database session.
        product (ProductPatch): The product to be patched.

    Returns:
        ProductResponse: The patched product.
    """

    return await update_product(session=session, product=product, product_id=product_id)


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
        product_id: int,
        session: SessionDep,
        _: None = Depends(is_admin)
):
    """
    Delete a product from the database.

    Args:
        product_id (int): The ID of the product to delete.
        session (SessionDep): The database session.

    Returns:
        dict: A message indicating the success or failure of the deletion.
    """

    remove_product(session=session, product_id=product_id)
