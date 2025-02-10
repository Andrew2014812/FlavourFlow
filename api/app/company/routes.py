from typing import List

from fastapi import APIRouter, Depends

from api.app.common.dependencies import SessionDep
from api.app.company.crud import (
    create_company,
    get_all_companies,
    get_company_by_id,
    update_company,
    remove_company,
)
from api.app.company.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyPatch,
)

router = APIRouter()


@router.get("/")
def company_list(
        session: SessionDep, page: int = 1, limit: int = 10
) -> List[CompanyResponse]:
    """
    Return a list of all companies.

    Args:
        session (SessionDep): A SQLAlchemy session object.
        page (int, optional): The page number of the companies to return, starting from 1. Defaults to 1.
        limit (int, optional): The number of companies to return per page. Defaults to 10.

    Returns:
        List[CompanyResponse]: A list of CompanyResponse objects representing the companies.
    """

    return get_all_companies(session=session, page=page, limit=limit)


@router.get("/{company_id}/")
def company_detail(company_id: int, session: SessionDep) -> CompanyResponse:
    """
    Retrieve details of a specific company by its ID.

    Args:
        company_id (int): The ID of the company to retrieve.
        session (SessionDep): A SQLAlchemy session object.

    Returns:
        CompanyResponse: An object containing the details of the specified company.
    """

    return get_company_by_id(session=session, company_id=company_id)


@router.post("/")
async def post_company(
        session: SessionDep, company: CompanyCreate = Depends(CompanyCreate.as_form)
) -> CompanyResponse:
    """
    Create a new company in the database.

    Args:
        session (SessionDep): A SQLAlchemy session object.
        company (CompanyCreate, optional): The company data to create. Defaults to data from form.

    Returns:
        CompanyResponse: An object containing the details of the newly created company.
    """

    return await create_company(session=session, company=company)


@router.put("/{company_id}/")
async def put_company(
        company_id: int,
        session: SessionDep,
        company: CompanyCreate = Depends(CompanyCreate.as_form),
) -> CompanyResponse:
    """
    Update a company in the database.

    Args:
        company_id (int): The ID of the company to update.
        session (SessionDep): A SQLAlchemy session object.
        company (CompanyCreate, optional): The new company data to update. Defaults to data from form.

    Returns:
        CompanyResponse: An object containing the details of the updated company.
    """

    return await update_company(session=session, company=company, company_id=company_id)


@router.patch("/{company_id}/")
async def patch_company(
        company_id: int,
        session: SessionDep,
        company: CompanyPatch = Depends(CompanyPatch.as_form),
) -> CompanyResponse:
    """
    Partially update a company's details in the database.

    Args:
        company_id (int): The ID of the company to update.
        session (SessionDep): A SQLAlchemy session object.
        company (CompanyPatch, optional): The partial company data to update. Defaults to data from form.

    Returns:
        CompanyResponse: An object containing the details of the updated company.
    """

    return await update_company(session=session, company=company, company_id=company_id)


@router.delete("/{company_id}/")
def delete_company(company_id: int, session: SessionDep) -> dict:
    """
    Delete a company from the database.

    Args:
        company_id (int): The ID of the company to delete.
        session (SessionDep): A SQLAlchemy session object.

    Returns:
        dict: A dictionary containing a message about the deletion.
    """

    return remove_company(session=session, company_id=company_id)
