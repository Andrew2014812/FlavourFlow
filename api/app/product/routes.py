from fastapi import APIRouter, UploadFile, File, Depends

from api.app.common.dependencies import SessionDep
from api.app.product.crud import create_product
from api.app.product.schemas import ProductCreate, ProductResponse

router = APIRouter()


@router.post("/")
async def post_product(session: SessionDep,
                       product: ProductCreate = Depends(ProductCreate.as_form),
                       image: UploadFile = File(...)) -> ProductResponse:
    return await create_product(session=session, product=product, image=image)
