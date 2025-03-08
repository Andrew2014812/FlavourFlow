from typing import Callable, Dict, List, Optional, Tuple

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

user_categories: Dict[int, str] = {}


def create_button(
    text: str, callback_data: str, is_current: bool = False
) -> InlineKeyboardButton:
    display_text = f"[{text}]" if is_current else text
    return InlineKeyboardButton(text=display_text, callback_data=callback_data)


def get_navigation_buttons(
    current_page: int, total_pages: int, content_type: str, extra_arg: str = ""
) -> list[InlineKeyboardButton]:
    buttons = []
    base_prefix = f"{content_type}_page_"
    suffix = f"_{extra_arg}" if extra_arg else ""

    if current_page > 1:
        buttons.append(create_button("<-", f"{base_prefix}{current_page-1}{suffix}"))

    if current_page < total_pages:
        buttons.append(create_button("->", f"{base_prefix}{current_page+1}{suffix}"))

    return buttons


def get_page_buttons(
    current_page: int, total_pages: int, content_type: str, extra_arg: str = ""
) -> List[InlineKeyboardButton]:
    buttons = []
    base_prefix = f"{content_type}_page_"
    suffix = f"_{extra_arg}" if extra_arg else ""

    if total_pages <= 5:
        buttons.extend(
            create_button(str(i), f"{base_prefix}{i}{suffix}", i == current_page)
            for i in range(1, total_pages + 1)
        )
    elif current_page <= 3:
        buttons.extend(
            create_button(str(i), f"{base_prefix}{i}{suffix}", i == current_page)
            for i in range(1, 4)
        )
        if total_pages > 3:
            buttons.extend(
                [
                    InlineKeyboardButton(text="...", callback_data="noop"),
                    create_button(
                        str(total_pages - 1), f"{base_prefix}{total_pages-1}{suffix}"
                    ),
                    create_button(
                        str(total_pages), f"{base_prefix}{total_pages}{suffix}"
                    ),
                ]
            )
    elif current_page >= total_pages - 2:
        buttons.extend(
            [
                create_button("1", f"{base_prefix}1{suffix}"),
                InlineKeyboardButton(text="...", callback_data="noop"),
            ]
        )
        buttons.extend(
            create_button(str(i), f"{base_prefix}{i}{suffix}", i == current_page)
            for i in range(total_pages - 2, total_pages + 1)
        )
    else:
        buttons.extend(
            [
                create_button("1", f"{base_prefix}1{suffix}"),
                InlineKeyboardButton(text="...", callback_data="noop"),
                create_button(
                    str(current_page), f"{base_prefix}{current_page}{suffix}", True
                ),
                InlineKeyboardButton(text="...", callback_data="noop"),
                create_button(str(total_pages), f"{base_prefix}{total_pages}{suffix}"),
            ]
        )
    return buttons


def get_pagination_keyboard(
    current_page: int, total_pages: int, content_type: str, extra_arg: str = ""
) -> InlineKeyboardMarkup:
    buttons = get_navigation_buttons(current_page, total_pages, content_type, extra_arg)
    page_buttons = get_page_buttons(current_page, total_pages, content_type, extra_arg)

    if buttons and len(buttons) == 2:
        buttons[1:1] = page_buttons

    elif buttons and buttons[0].text == "<-":
        buttons[1:] = page_buttons

    else:
        buttons[0:0] = page_buttons

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def create_pagination_handler(content_type: str, render_content: Callable):
    async def handler(callback: CallbackQuery, language_code: str):
        if callback.data.startswith(f"{content_type}_page_"):
            parts = callback.data.split("_")
            page = int(parts[2])
            extra_arg = parts[3] if len(parts) > 3 else ""

            if extra_arg:
                caption, image_url, total_pages = render_content(
                    page, language_code, extra_arg
                )
            else:
                caption, image_url, total_pages = render_content(page, language_code)

            keyboard = get_pagination_keyboard(
                page, total_pages, content_type, extra_arg
            )

            if image_url:
                await callback.message.edit_media(
                    InputMediaPhoto(media=image_url, caption=caption),
                    reply_markup=keyboard,
                )
            else:
                await callback.message.edit_text(caption, reply_markup=keyboard)

        await callback.answer()

    return handler


def get_category_keyboard() -> InlineKeyboardMarkup:
    categories = [
        InlineKeyboardButton(text="Tech", callback_data="category_tech"),
        InlineKeyboardButton(text="Retail", callback_data="category_retail"),
        InlineKeyboardButton(text="Finance", callback_data="category_finance"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[categories])


def render_company_content(
    page: int, language_code: str, category: str
) -> Tuple[str, Optional[str], int]:
    total_pages = 15
    image_url = (
        "https://i.pinimg.com/736x/bd/e5/64/bde56448f3661d1ea72631c07e400338.jpg"
    )
    caption = f"Company listing ({category}) - Page {page} of {total_pages} (lang: {language_code})"
    return caption, image_url, total_pages


def render_product_content(
    page: int, language_code: str
) -> Tuple[str, Optional[str], int]:
    total_pages = 20
    image_url = None
    content = f"Product catalog - Page {page} of {total_pages} (lang: {language_code})"
    return content, image_url, total_pages


company_handler = create_pagination_handler("company", render_company_content)
product_handler = create_pagination_handler("product", render_product_content)
