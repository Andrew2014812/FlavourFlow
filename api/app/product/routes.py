from typing import List

from fastapi import APIRouter, UploadFile, File, Depends

from api.app.common.dependencies import SessionDep
from api.app.product.crud import create_product, get_all_products, get_product_by_id, update_product, remove_product
from api.app.product.schemas import ProductCreate, ProductResponse, ProductPatch

router = APIRouter()


@router.get("/")
def product_list(
        session: SessionDep, page: int = 1, limit: int = 10
) -> List[ProductResponse]:
    return get_all_products(session=session, page=page, limit=limit)


@router.get("/{product_id}/")
def company_detail(product_id: int, session: SessionDep) -> ProductResponse:
    return get_product_by_id(session=session, product_id=product_id)


@router.post("/")
async def post_product(session: SessionDep,
                       product: ProductCreate = Depends(ProductCreate.as_form)) -> ProductResponse:
    return await create_product(session=session, product=product)


@router.put("/{product_id}/")
async def put_company(
        product_id: int, session: SessionDep, product: ProductCreate = Depends(ProductCreate.as_form)
) -> ProductResponse:
    return await update_product(session=session, product=product, product_id=product_id)


@router.patch("/{product_id}/")
async def patch_company(
        product_id: int, session: SessionDep, product: ProductPatch = Depends(ProductPatch.as_form)
) -> ProductResponse:
    return await update_product(session=session, product=product, product_id=product_id)


@router.delete("/{product_id}/")
def delete_company(product_id: int, session: SessionDep) -> dict:
    return remove_product(session=session, product_id=product_id)
