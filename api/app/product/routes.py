from fastapi import APIRouter, Depends, status

from ..common.dependencies import SessionDep
from ..product.crud import (
    create_product,
    get_all_products,
    get_product_by_id,
    remove_product,
    update_product,
)
from ..product.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductPatch,
    ProductResponse,
)
from ..user.crud import is_admin

router = APIRouter()


@router.get("/")
async def product_list(
    session: SessionDep,
    page: int = 1,
    limit: int = 10,
    company_id: int = None,
) -> ProductListResponse:
    return await get_all_products(
        session=session,
        page=page,
        limit=limit,
        company_id=company_id,
    )


@router.get("/{product_id}/")
async def product_detail(product_id: int, session: SessionDep) -> ProductResponse:

    return await get_product_by_id(session=session, product_id=product_id)


@router.post("/")
async def post_product(
    session: SessionDep,
    product: ProductCreate = Depends(ProductCreate.as_form),
    _: None = Depends(is_admin),
) -> ProductResponse:

    return await create_product(session=session, product_create=product)


@router.put("/{product_id}/")
async def put_product(
    product_id: int,
    session: SessionDep,
    product: ProductCreate = Depends(ProductCreate.as_form),
    _: None = Depends(is_admin),
) -> ProductResponse:

    return await update_product(session=session, product=product, product_id=product_id)


@router.patch("/{product_id}/")
async def patch_product(
    product_id: int,
    session: SessionDep,
    product: ProductPatch = Depends(ProductPatch.as_form),
    _: None = Depends(is_admin),
) -> ProductResponse:

    return await update_product(session=session, product=product, product_id=product_id)


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int, session: SessionDep, _: None = Depends(is_admin)
):

    await remove_product(session=session, product_id=product_id)
