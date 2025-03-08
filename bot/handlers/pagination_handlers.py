from typing import Callable, List, Tuple

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


def create_button(
    text: str, callback_data: str, is_current: bool = False
) -> InlineKeyboardButton:
    display_text = f"[{text}]" if is_current else text
    return InlineKeyboardButton(text=display_text, callback_data=callback_data)


def get_navigation_buttons(
    current_page: int, total_pages: int, content_type: str
) -> List[InlineKeyboardButton]:
    buttons = []

    if current_page > 1:
        buttons.append(create_button("<-", f"{content_type}_page_{current_page-1}"))

    if current_page < total_pages:
        buttons.append(create_button("->", f"{content_type}_page_{current_page+1}"))

    return buttons


def get_page_buttons(
    current_page: int, total_pages: int, content_type: str
) -> List[InlineKeyboardButton]:
    buttons = []

    if current_page <= 3:
        buttons.extend(
            create_button(str(i), f"{content_type}_page_{i}", i == current_page)
            for i in range(1, min(4, total_pages + 1))
        )
        if total_pages > 5:
            buttons.extend(
                [
                    InlineKeyboardButton(text="...", callback_data="noop"),
                    create_button(
                        str(total_pages - 1), f"{content_type}_page_{total_pages-1}"
                    ),
                    create_button(
                        str(total_pages), f"{content_type}_page_{total_pages}"
                    ),
                ]
            )

    elif current_page <= total_pages - 2:
        buttons.extend(
            [
                create_button("1", f"{content_type}_page_1"),
                InlineKeyboardButton(text="...", callback_data="noop"),
                create_button(
                    str(current_page), f"{content_type}_page_{current_page}", True
                ),
                InlineKeyboardButton(text="...", callback_data="noop"),
                create_button(
                    str(total_pages - 1), f"{content_type}_page_{total_pages-1}"
                ),
                create_button(str(total_pages), f"{content_type}_page_{total_pages}"),
            ]
        )

    else:
        buttons.extend(
            [
                create_button("1", f"{content_type}_page_1"),
                InlineKeyboardButton(text="...", callback_data="noop"),
            ]
        )

        buttons.extend(
            create_button(str(i), f"{content_type}_page_{i}", i == current_page)
            for i in range(total_pages - 2, total_pages + 1)
        )

    return buttons


def get_pagination_keyboard(
    current_page: int, total_pages: int, content_type: str
) -> InlineKeyboardMarkup:
    buttons = get_navigation_buttons(current_page, total_pages, content_type)
    page_buttons = get_page_buttons(current_page, total_pages, content_type)

    if buttons and len(buttons) == 2:
        buttons[1:1] = page_buttons

    elif buttons and buttons[0].text == "<-":
        buttons[1:] = page_buttons

    else:
        buttons[0:0] = page_buttons

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


ContentRenderer = Callable[[int, str], Tuple[str, int]]


def create_pagination_handler(content_type: str, render_content: ContentRenderer):
    async def handler(callback: CallbackQuery, language_code: str):
        if callback.data.startswith(f"{content_type}_page_"):
            page = int(callback.data.split("_")[2])
            content, total_pages = render_content(page, language_code)

            await callback.message.edit_text(
                content,
                reply_markup=get_pagination_keyboard(page, total_pages, content_type),
            )
        await callback.answer()

    return handler


def render_company_content(page: int, language_code: str) -> Tuple[str, int]:
    total_pages = 15
    content = f"Company listing - Page {page} of {total_pages} (lang: {language_code})"
    return content, total_pages


def render_product_content(page: int, language_code: str) -> Tuple[str, int]:
    total_pages = 20
    content = f"Product catalog - Page {page} of {total_pages} (lang: {language_code})"
    return content, total_pages


company_handler = create_pagination_handler("company", render_company_content)
product_handler = create_pagination_handler("product", render_product_content)
