import random

from cloudinary.exceptions import GeneralError
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..common.dependencies import SessionDep
from ..company.models import Company
from ..product.models import Product
from ..product.schemas import ProductCreate, ProductListResponse, ProductResponse
from ..user.models import User
from ..utils import delete_file, get_entity_by_params, upload_file

PRODUCT_NOT_FOUND = "Product not found"


async def create_product(
    session: SessionDep, product_create: ProductCreate
) -> ProductResponse:
    statement = select(Product).filter(
        Product.title_ua == product_create.title_ua,
        Product.title_en == product_create.title_en,
    )

    result = await session.exec(statement)
    existing_product = result.first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists"
        )

    db_product = Product()

    for key, value in product_create.model_dump(exclude="image").items():
        setattr(db_product, key, value)

    session.add(db_product)
    await session.flush()

    try:
        image_name = f"PRODUCT_ID-{db_product.id}"
        image_data: dict = await upload_file(
            filename=image_name, folder="product", file=product_create.image
        )

        db_product.image_id = image_data.get("image_id")
        db_product.image_link = image_data.get("url")

        await session.commit()
    except GeneralError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Failed to create a product. Error during file upload.",
        )

    await session.refresh(db_product)
    return db_product


async def get_all_products(
    session: SessionDep,
    page: int = 1,
    limit: int = 10,
    company_id: int = None,
) -> ProductListResponse:
    products, total_pages = await get_entity_by_params(
        session,
        Product,
        page=page,
        limit=limit,
        company_id=company_id,
        return_all=True,
        with_total_pages=True,
    )

    return ProductListResponse(products=products, total_pages=total_pages)


async def get_product_by_id(session: SessionDep, product_id: int) -> ProductResponse:
    statement = select(Product).filter(Product.id == product_id)
    result = await session.exec(statement)
    db_product = result.first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    return db_product


async def update_product(
    session: SessionDep,
    product: ProductCreate,
    product_id: int,
) -> ProductResponse:
    statement = select(Product).where(Product.id == product_id)
    result = await session.exec(statement)
    existing_product: Product = result.first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    if product.image:
        result = await delete_file(existing_product.image_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The image could not be replaced",
            )

        image_name = f"PRODUCT_ID-{existing_product.id}"
        image_data: dict = await upload_file(
            filename=image_name, folder="product", file=product.image
        )
        existing_product.image_link = image_data.get("url")
        existing_product.image_id = image_data.get("image_id")

    update_data = {
        k: v
        for k, v in product.model_dump(exclude_unset=True, exclude={"image"}).items()
        if v is not None
    }
    for key, value in update_data.items():
        setattr(existing_product, key, value)

    await session.merge(existing_product)
    await session.commit()
    await session.refresh(existing_product)

    return existing_product


async def remove_product(session: SessionDep, product_id: int):
    statement = select(Product).where(Product.id == product_id)
    result = await session.exec(statement)
    existing_product: Product = result.first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    result = await delete_file(existing_product.image_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The image could not be deleted",
        )

    await session.delete(existing_product)
    await session.commit()


async def get_product_recommendations(
    session: SessionDep,
    user: User,
) -> ProductListResponse:
    if not user.orders:
        companies = await get_entity_by_params(
            session,
            Company,
            return_all=True,
        )
        companies_ids = [company.id for company in companies]

        if not companies_ids:
            return ProductListResponse(products=[], total_pages=1)

        target_company_id = random.choice(companies_ids)

        products = await get_entity_by_params(
            session,
            Product,
            return_all=True,
            filters={"company_id": target_company_id},
        )

        random_products = random.sample(products, min(2, len(products)))
        products_result = [
            ProductResponse(
                **product.model_dump(),
                company_name_en=product.company.title_en,
                company_name_ua=product.company.title_ua,
            )
            for product in random_products
        ]

        return ProductListResponse(products=products_result, total_pages=1)

    else:
        order_company_ids = list(set(order.company_id for order in user.orders))
        target_company_id = random.choice(order_company_ids)

        used_product_ids = set(
            item.product_id for order in user.orders for item in order.order_items
        )

        all_products = await get_entity_by_params(
            session,
            Product,
            return_all=True,
            filters={"company_id": target_company_id},
            options=[joinedload(Product.company)],
        )

        available_products = [
            product for product in all_products if product.id not in used_product_ids
        ]

        if not available_products:
            companies = await get_entity_by_params(
                session,
                Company,
                return_all=True,
            )
            companies_ids = [company.id for company in companies]

            if not companies_ids:
                return ProductListResponse(products=[], total_pages=1)

            target_company_id = random.choice(companies_ids)

            products = await get_entity_by_params(
                session,
                Product,
                return_all=True,
                filters={"company_id": target_company_id},
            )

            random_products = random.sample(products, min(2, len(products)))

            products_result = [
                ProductResponse(
                    **product.model_dump(),
                    company_name_en=product.company.title_en,
                    company_name_ua=product.company.title_ua,
                )
                for product in random_products
            ]
            return ProductListResponse(products=products_result, total_pages=1)

        random_products = random.sample(
            available_products, min(2, len(available_products))
        )

        products_result = [
            ProductResponse(
                **product.model_dump(),
                company_name_en=product.company.title_en,
                company_name_ua=product.company.title_ua,
            )
            for product in random_products
        ]
        return ProductListResponse(products=products_result, total_pages=1)
