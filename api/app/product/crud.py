from typing import List

from cloudinary.exceptions import GeneralError
from fastapi import HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.product.models import Product
from api.app.product.schemas import ProductCreate, ProductResponse
from api.app.utils import upload_file, delete_file

PRODUCT_NOT_FOUND = "Product not found"


async def create_product(session: SessionDep, product_create: ProductCreate) -> ProductResponse:
    statement = select(Product).filter(
        Product.title_ua == product_create.title_ua,
        Product.title_en == product_create.title_en,
    )

    existing_product = session.exec(statement).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists"
        )

    db_product = Product()

    for key, value in product_create.model_dump(exclude='image').items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.flush()

    try:
        image_name = f'PRODUCT_ID-{db_product.id}'
        image_data: dict = await upload_file(filename=image_name, folder='product', file=product_create.image)

        db_product.image_id = image_data.get('image_id')
        db_product.image_link = image_data.get('url')

        session.commit()
    except GeneralError:
        session.rollback()

        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail="Failed to create a product. Error during file upload.")

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


async def update_product(
        session: SessionDep, product: ProductCreate, product_id: int
) -> ProductResponse:
    existing_product: Product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    if product.image:
        result = delete_file(existing_product.image_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image could not be replaced")

        image_name = f'PRODUCT_ID-{existing_product.id}'
        image_data: dict = await upload_file(filename=image_name, folder='product', file=product.image)
        existing_product.image_link = image_data.get('url')
        existing_product.image_id = image_data.get('image_id')

    update_data = {k: v for k, v in product.model_dump(exclude_unset=True, exclude={'image'}).items() if v is not None}
    for key, value in update_data.items():
        setattr(existing_product, key, value)

    session.merge(existing_product)
    session.commit()
    session.refresh(existing_product)

    return existing_product


def remove_product(session: SessionDep, product_id: int):
    existing_product: Product = session.exec(
        select(Product).where(Product.id == product_id)
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PRODUCT_NOT_FOUND
        )

    result = delete_file(existing_product.image_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image could not be deleted")

    session.delete(existing_product)
    session.commit()
