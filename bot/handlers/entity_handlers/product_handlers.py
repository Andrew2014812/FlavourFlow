from typing import Optional, Tuple


def render_product_content(
    page: int, language_code: str
) -> Tuple[str, Optional[str], int]:
    total_pages = 20
    image_url = None
    content = f"Product catalog - Page {page} of {total_pages} (lang: {language_code})"
    return content, image_url, total_pages
