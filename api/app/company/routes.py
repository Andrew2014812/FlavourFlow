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
    return get_all_companies(session=session, page=page, limit=limit)


@router.get("/{company_id}/")
def company_detail(company_id: int, session: SessionDep) -> CompanyResponse:
    return get_company_by_id(session=session, company_id=company_id)


@router.post("/")
async def post_company(session: SessionDep,
                       company: CompanyCreate = Depends(CompanyCreate.as_form)) -> CompanyResponse:
    return await create_company(session=session, company=company)


@router.put("/{company_id}/")
async def put_company(
        company_id: int, session: SessionDep, company: CompanyCreate = Depends(CompanyCreate.as_form)
) -> CompanyResponse:
    return await update_company(session=session, company=company, company_id=company_id)


@router.patch("/{company_id}/")
async def patch_company(
        company_id: int, session: SessionDep, company: CompanyPatch = Depends(CompanyPatch.as_form)
) -> CompanyResponse:
    return await update_company(session=session, company=company, company_id=company_id)


@router.delete("/{company_id}/")
def delete_company(company_id: int, session: SessionDep) -> dict:
    return remove_company(session=session, company_id=company_id)
