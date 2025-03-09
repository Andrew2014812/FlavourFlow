from typing import Optional, Tuple

from ...common.services.country_service import CountryListResponse, get_country_list
from .buttons_util import build_admin_buttons


async def render_country_content(
    page: int, language_code: str
) -> Tuple[str, Optional[str], int]:
    result = await get_country_list()
    country_list_response: CountryListResponse = result
    total_pages = country_list_response.total_pages

    if language_code == "ua":
        country_titles = [
            country.title_ua for country in country_list_response.countries
        ]
    else:
        country_titles = [
            country.title_en for country in country_list_response.countries
        ]

    result = await build_admin_buttons(country_titles, "country", page, language_code)
    builder = result

    text = f"Category listing - Page {page} of {total_pages} (lang: {language_code})"
    return text, None, total_pages, builder
