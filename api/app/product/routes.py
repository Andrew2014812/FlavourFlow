from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import joinedload

from ..common.dependencies import SessionDep
from ..order.models import Order, OrderItem
from ..product.crud import (
    create_product,
    get_all_products,
    get_product_by_id,
    get_product_recommendations,
    remove_product,
    update_product,
)
from ..product.models import Product
from ..product.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductPatch,
    ProductResponse,
)
from ..user.crud import get_current_user, is_admin
from ..user.models import User
from ..utils import get_entity_by_params

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


@router.get("/recommendations/")
async def get_recommendations(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> ProductListResponse:
    user = await get_entity_by_params(
        session=session,
        entity_class=User,
        id=current_user.id,
        options=[
            joinedload(User.orders),
            joinedload(User.orders).joinedload(Order.order_items),
            joinedload(User.orders)
            .joinedload(Order.order_items)
            .joinedload(OrderItem.product),
            joinedload(User.orders)
            .joinedload(Order.order_items)
            .joinedload(OrderItem.product)
            .joinedload(Product.company),
        ],
        return_all=False,
    )
    return await get_product_recommendations(
        session=session,
        user=user,
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
