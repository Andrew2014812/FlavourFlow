from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.product.models import Product
from api.app.product.schemas import ProductCreate, ProductResponse
from api.app.utils import upload_file

PRODUCT_NOT_FOUND = "Product not found"


async def create_product(session: SessionDep, product: ProductCreate, image: UploadFile) -> ProductResponse:
    existing_product = session.exec(
        select(Product).filter(Product.title == product.title)
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists"
        )

    image_name = f'{product.title}.png'
    image_data: dict = await upload_file(image_name, image)

    db_product = Product(
        title=product.title,
        description=product.description,
        composition=product.composition,
        product_category=product.product_category,
        price=product.price,
        image_link=image_data.get('url'),
        image_id=image_data.get('image_id'),
        company_id=product.company_id,
    )

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return db_product


def get_all_products(
        session: SessionDep, page: int = 1, limit: int = 10
) -> List[ProductResponse]:
    return session.exec(select(Product).limit(limit).offset((page - 1) * limit)).all()


def get_product_by_id(session: SessionDep, product_id: int) -> ProductResponse:
    db_product = session.exec(select(Product).filter(Product.id == product_id)).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    return db_product
