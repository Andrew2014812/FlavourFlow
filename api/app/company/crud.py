from cloudinary.exceptions import GeneralError
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from ..common.dependencies import SessionDep
from ..company.models import Company
from ..company.schemas import (
    CompanyCreate,
    CompanyListResponse,
    CompanyPatch,
    CompanyResponse,
)
from ..product.crud import remove_product
from ..utils import delete_file, upload_file

COMPANY_NOT_FOUND = "Company not found"


async def create_company(
    session: SessionDep, company_create: CompanyCreate
) -> CompanyResponse:
    statement = select(Company).filter(
        Company.title_ua == company_create.title_ua,
        Company.title_en == company_create.title_en,
    )

    result = await session.exec(statement)
    existing_company: Company = result.first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists"
        )

    db_company = Company()

    for key, value in company_create.model_dump(exclude="image").items():
        setattr(db_company, key, value)

    session.add(db_company)
    await session.flush()

    try:
        image_name = f"COMPANY_ID-{db_company.id}"
        image_data: dict = await upload_file(
            filename=image_name, folder="company", file=company_create.image
        )

        db_company.image_id = image_data.get("image_id")
        db_company.image_link = image_data.get("url")

        await session.commit()

    except GeneralError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Failed to create a company. Error during file upload.",
        )

    await session.refresh(db_company)
    return db_company


async def get_all_companies(
    session: SessionDep,
    page: int = 1,
    limit: int = 6,
) -> CompanyListResponse:
    statement = select(func.count()).select_from(Company)
    result = await session.exec(statement)
    total_records = result.one()

    total_pages = (total_records + limit - 1) // limit

    statement = select(Company).limit(limit).offset((page - 1) * limit)
    result = await session.exec(statement)
    companies = result.all()

    return CompanyListResponse(companys=companies, total_pages=total_pages)


async def get_company_by_id(session: SessionDep, company_id: int) -> CompanyResponse:
    statement = select(Company).filter(Company.id == company_id)
    result = await session.exec(statement)
    db_company = result.first()

    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    return db_company


async def update_company(
    session: SessionDep, company: CompanyCreate | CompanyPatch, company_id: int
) -> CompanyResponse:
    statement = select(Company).where(Company.id == company_id)
    result = await session.exec(statement)
    existing_company: Company = result.first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    if company.image:
        result = delete_file(existing_company.image_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The image could not be replaced",
            )

        image_name = f"COMPANY_ID-{existing_company.id}"
        image_data: dict = await upload_file(
            filename=image_name, folder="company", file=company.image
        )
        existing_company.image_id = image_data.get("image_id")
        existing_company.image_link = image_data.get("url")

    update_data = {
        k: v
        for k, v in company.model_dump(exclude_unset=True, exclude={"image"}).items()
        if v is not None
    }
    for key, value in update_data.items():
        setattr(existing_company, key, value)

    await session.merge(existing_company)
    await session.commit()
    await session.refresh(existing_company)

    return existing_company


async def remove_company(session: SessionDep, company_id: int):
    statement = (
        select(Company)
        .where(Company.id == company_id)
        .options(selectinload(Company.products))
    )
    result = await session.exec(statement)
    existing_company: Company = result.first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    result = await delete_file(existing_company.image_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The image could not be deleted",
        )

    if existing_company.products:
        for product in existing_company.products:
            await remove_product(session, product.id)

    await session.delete(existing_company)
    await session.commit()
