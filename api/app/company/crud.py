from typing import List

from cloudinary.exceptions import GeneralError
from fastapi import HTTPException, status
from sqlmodel import select, func

from api.app.common.dependencies import SessionDep
from api.app.company.models import Company
from api.app.company.schemas import CompanyCreate, CompanyResponse, CompanyPatch
from api.app.product.crud import remove_product
from api.app.utils import upload_file, delete_file

COMPANY_NOT_FOUND = "Company not found"


async def create_company(session: SessionDep, company_create: CompanyCreate) -> CompanyResponse:
    statement = select(Company).filter(
        Company.title_ua == company_create.title_ua,
        Company.title_en == company_create.title_en
    )

    existing_company = session.exec(statement).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists"
        )

    db_company = Company()

    for key, value in company_create.model_dump(exclude='image').items():
        setattr(db_company, key, value)

    session.add(db_company)
    session.commit()
    session.refresh(db_company)

    try:
        image_name = f'COMPANY_ID-{db_company.id}'
        image_data: dict = await upload_file(filename=image_name, folder='company', file=company_create.image)

        db_company.image_id = image_data.get('image_id')
        db_company.image_link = image_data.get('url')

        session.commit()

    except GeneralError:
        session.rollback()
        session.delete(db_company)
        session.commit()

        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                            detail="Failed to create a company. Error during file upload.")

    return db_company


def get_all_companies(
        session: SessionDep, page: int = 1, limit: int = 10
) -> tuple[List[CompanyResponse], int]:
    total_records = session.exec(select(func.count()).select_from(Company)).one()

    total_pages = (total_records + limit - 1) // limit

    companies = session.exec(
        select(Company).limit(limit).offset((page - 1) * limit)
    ).all()

    return companies, total_pages


def get_company_by_id(session: SessionDep, company_id: int) -> CompanyResponse:
    db_company = session.exec(select(Company).filter(Company.id == company_id)).first()

    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    return db_company


async def update_company(
        session: SessionDep, company: CompanyCreate | CompanyPatch, company_id: int
) -> CompanyResponse:
    existing_company: Company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    if company.image:
        result = delete_file(existing_company.image_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image could not be replaced")

        image_name = f'COMPANY_ID-{existing_company.id}'
        image_data: dict = await upload_file(filename=image_name, folder='company', file=company.image)
        existing_company.image_id = image_data.get('image_id')
        existing_company.image_link = image_data.get('url')

    update_data = {k: v for k, v in company.model_dump(exclude_unset=True, exclude={'image'}).items() if v is not None}
    for key, value in update_data.items():
        setattr(existing_company, key, value)

    session.merge(existing_company)
    session.commit()
    session.refresh(existing_company)

    return existing_company


def remove_company(session: SessionDep, company_id: int):
    existing_company: Company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    result = delete_file(existing_company.image_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image could not be deleted")

    if existing_company.products:
        for product in existing_company.products:
            remove_product(session, product.id)

    session.delete(existing_company)
    session.commit()
