from typing import List

from fastapi import APIRouter, Depends, status

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
from api.app.user.crud import is_admin

router = APIRouter()


@router.get("/")
async def company_list(
        session: SessionDep,
        page: int = 1,
        limit: int = 10,
) -> tuple[List[CompanyResponse], int]:
    """
    Retrieve a list of all companies.

    Args:
        session (SessionDep): The database session.
        page (int, optional): The page number. Defaults to 1.
        limit (int, optional): The page size. Defaults to 10.

    Returns:
        List[CompanyResponse]: A list of company details.
    """

    return await get_all_companies(session=session, page=page, limit=limit)


@router.get("/{company_id}/")
async def company_detail(
        company_id: int,
        session: SessionDep,
) -> CompanyResponse:
    """
    Retrieve a company by its ID.

    Args:
        company_id (int): The ID of the company to retrieve.
        session (SessionDep): The database session.

    Returns:
        CompanyResponse: The retrieved company.
    """

    return await get_company_by_id(session=session, company_id=company_id)


@router.post("/")
async def post_company(
        session: SessionDep,
        company: CompanyCreate = Depends(CompanyCreate.as_form),
        _: None = Depends(is_admin),
) -> CompanyResponse:
    """
    Create a new company in the database.

    Args:
        session (SessionDep): The database session.
        company (CompanyCreate): The company to be created.

    Returns:
        CompanyResponse: The created company.
    """
    created_company = await create_company(session=session, company_create=company)
    return created_company


@router.put("/{company_id}/")
async def put_company(
        company_id: int,
        session: SessionDep,
        company: CompanyCreate = Depends(CompanyCreate.as_form),
        _: None = Depends(is_admin),
) -> CompanyResponse:
    """
    Update an existing company in the database.

    Args:
        session (SessionDep): The database session.
        company_id (int): The ID of the company to update.
        company (CompanyCreate): The company details to update.

    Returns:
        CompanyResponse: The updated company.
    """

    return await update_company(session=session, company=company, company_id=company_id)


@router.patch("/{company_id}/")
async def patch_company(
        company_id: int,
        session: SessionDep,
        company: CompanyPatch = Depends(CompanyPatch.as_form),
        _: None = Depends(is_admin),
) -> CompanyResponse:
    """
    Partially update a company in the database.

    Args:
        session (SessionDep): The database session.
        company_id (int): The ID of the company to update.
        company (CompanyPatch): The company details to update.

    Returns:
        CompanyResponse: The updated company.
    """

    return await update_company(session=session, company=company, company_id=company_id)


@router.delete("/{company_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
        company_id: int,
        session: SessionDep,
        _: None = Depends(is_admin),
):
    """
    Delete a company from the database.

    Args:
        session (SessionDep): The database session.
        company_id (int): The ID of the company to delete.

    Returns:
        dict: A message indicating success or failure of the deletion.
    """

    await remove_company(session=session, company_id=company_id)
