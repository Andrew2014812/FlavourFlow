from typing import Optional, Tuple


def render_country_content(
    page: int, language_code: str
) -> Tuple[str, Optional[str], int]:

    caption = f"Company listing ({category}) - Page {page} of {total_pages} (lang: {language_code})"
    return caption, None, total_pages
