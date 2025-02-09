from typing import List

from fastapi import HTTPException, status, UploadFile
from sqlmodel import select

from api.app.common.dependencies import SessionDep
from api.app.company.models import Company
from api.app.company.schemas import CompanyCreate, CompanyResponse, CompanyUpdate
from api.app.utils import upload_file, delete_from_cloudinary

COMPANY_NOT_FOUND = "Company not found"


async def create_company(session: SessionDep, company: CompanyCreate, image: UploadFile) -> CompanyResponse:
    existing_company = session.exec(
        select(Company).filter(Company.title == company.title)
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists"
        )

    image_data: dict = await upload_file(image)

    db_company = Company(
        title=company.title,
        description=company.description,
        image_link=image_data.get('url'),
        image_id=image_data.get('image_id'),
        country_id=company.country_id,
        kitchen_id=company.kitchen_id,
    )

    session.add(db_company)
    session.commit()
    session.refresh(db_company)

    return db_company


def get_all_companies(
        session: SessionDep, page: int = 1, limit: int = 10
) -> List[CompanyResponse]:
    return session.exec(select(Company).limit(limit).offset((page - 1) * limit)).all()


def get_company_by_id(session: SessionDep, company_id: int) -> CompanyResponse:
    db_company = session.exec(select(Company).filter(Company.id == company_id)).first()

    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    return db_company


def update_company(
        session: SessionDep, company: CompanyUpdate, company_id: int
) -> CompanyResponse:
    existing_company: Company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    for key, value in company.model_dump(exclude_unset=True).items():
        setattr(existing_company, key, value)

    session.merge(existing_company)
    session.commit()
    session.refresh(existing_company)

    return existing_company


def remove_company(session: SessionDep, company_id: int) -> CompanyResponse:
    existing_company: Company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()

    if not existing_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=COMPANY_NOT_FOUND
        )

    result = delete_from_cloudinary(existing_company.image_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image could not be deleted")

    session.delete(existing_company)
    session.commit()

    return {"message": "Company deleted successfully", "company_id": company_id}
