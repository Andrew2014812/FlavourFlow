from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.product.models import Product
from api.app.product.schemas import ProductCreate, ProductResponse
from api.app.utils import upload_file, delete_file

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
    image_data: dict = await upload_file(filename=image_name, folder='product', file=image)

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

        image_name = f'{product.title if product.title else existing_product.title}.png'
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


def remove_product(session: SessionDep, product_id: int) -> ProductResponse:
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

    return {"message": "Product deleted successfully", "product_id": product_id}
