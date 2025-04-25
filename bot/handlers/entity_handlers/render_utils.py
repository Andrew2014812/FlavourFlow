from typing import Optional, Tuple

from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...common.services.company_service import company_service
from ...common.services.gastronomy_service import country_service, kitchen_service
from .handler_utils import build_admin_buttons

SERVICES = {
    "company": company_service,
    "country": country_service,
    "kitchen": kitchen_service,
}


async def render_admin_list(
    entity_type: str, page: int, language_code: str
) -> Tuple[str, None, int, InlineKeyboardBuilder]:
    service = SERVICES[entity_type]
    result = await service.get_list(page)
    total_pages = result.total_pages
    items = getattr(result, f"{entity_type}s")
    items_dict = {item.id: f"{item.title_ua} / {item.title_en}" for item in items}

    builder = await build_admin_buttons(
        items_dict, f"admin-{entity_type}", language_code, page
    )
    text = f"{entity_type.capitalize()} - Page {page} of {total_pages}"
    return text, None, total_pages, builder


async def render_company_list(
    page: int, language_code: str, kitchen_id: str
) -> Tuple[str, Optional[str], int, None]:
    result = await company_service.get_list(page=page, limit=1)
    total_pages = result.total_pages
    if not result.companys:
        return "No companies found", None, 1, None

    company = result.companys[0]
    text = (
        f"Company ({kitchen_id}) - Page {page} of {total_pages} (lang: {language_code})"
    )
    return text, company.image_link, total_pages, None
