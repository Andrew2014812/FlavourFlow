from enum import Enum
from io import BytesIO
from typing import Dict, Optional

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from api.app.common.database import engine
from api.app.product.crud import create_product
from api.app.product.schemas import ProductCreate, ProductListResponse, ProductResponse

from ...common.services.user_info_service import get_user_info
from ...config import APIAuth, APIMethods
from ..utils import make_request


class ProductEndpoints(Enum):
    BASE = "product/"


class ProductService:
    def __init__(self):
        self.prefix = "product/"

    async def get_list(
        self, company_id: int, page: int = 1, limit: int = 6
    ) -> Optional[ProductListResponse]:
        response = await make_request(
            sub_url=self.prefix,
            method=APIMethods.GET.value,
            params={"page": page, "limit": limit, "company_id": company_id},
        )
        return ProductListResponse.model_validate(response.get("data"))

    async def get_item(self, item_id: int) -> Optional[ProductResponse]:
        response = await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.GET.value,
        )
        return ProductResponse.model_validate(response.get("data"))

    async def create(self, data: Dict, image_bytes: bytes) -> Optional[ProductResponse]:
        image_file = UploadFile(filename="image.jpg", file=BytesIO(image_bytes))

        product_create_data = {
            **data,
            "image": image_file,
        }
        product_create = ProductCreate(**product_create_data)

        async with AsyncSession(engine) as session:
            response = await create_product(
                session=session, product_create=product_create
            )

    async def update(
        self, item_id: int, data: Dict, telegram_id: int
    ) -> Optional[ProductResponse]:
        user_info = await get_user_info(telegram_id)
        response = await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.PATCH.value,
            data=data,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )
        return ProductResponse.model_validate(response.get("data"))

    async def delete(self, item_id: int, telegram_id: int) -> None:
        user_info = await get_user_info(telegram_id)
        await make_request(
            sub_url=f"{self.prefix}{item_id}/",
            method=APIMethods.DELETE.value,
            headers={
                APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
            },
        )


product_service = ProductService()
