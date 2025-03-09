import json
from typing import Callable, List

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

left_arrow = "⬅️"
right_arrow = "➡️"
middle_button = "🔘"

from bot.handlers.entity_handlers.category_handlers import render_country_content
from bot.handlers.entity_handlers.company_handlers import (
    render_company_content,
    render_company_content_for_admin,
)
from bot.handlers.entity_handlers.product_handlers import render_product_content


def create_button(
    button_text: str, callback_data: str, is_current: bool = False
) -> InlineKeyboardButton:
    display_text = f"[{button_text}]" if is_current else button_text
    return InlineKeyboardButton(text=display_text, callback_data=callback_data)


def get_navigation_buttons(
    current_page: int, total_pages: int, content_type: str, extra_arg: str = ""
) -> list[InlineKeyboardButton]:
    buttons = []
    base_prefix = f"{content_type}_page_"
    suffix = f"_{extra_arg}" if extra_arg else ""

    if current_page > 1:
        buttons.append(
            create_button(left_arrow, f"{base_prefix}{current_page-1}{suffix}")
        )

    if current_page < total_pages:
        buttons.append(
            create_button(right_arrow, f"{base_prefix}{current_page+1}{suffix}")
        )

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
            middle_page = total_pages // 2
            buttons.extend(
                [
                    InlineKeyboardButton(
                        text=middle_button,
                        callback_data=f"{base_prefix}{middle_page}{suffix}",
                    ),
                    create_button(
                        str(total_pages - 1), f"{base_prefix}{total_pages-1}{suffix}"
                    ),
                    create_button(
                        str(total_pages), f"{base_prefix}{total_pages}{suffix}"
                    ),
                ]
            )
    elif current_page >= total_pages - 2:
        middle_page = total_pages // 2
        buttons.extend(
            [
                create_button("1", f"{base_prefix}1{suffix}"),
                InlineKeyboardButton(
                    text=middle_button,
                    callback_data=f"{base_prefix}{middle_page}{suffix}",
                ),
            ]
        )
        buttons.extend(
            create_button(str(i), f"{base_prefix}{i}{suffix}", i == current_page)
            for i in range(total_pages - 2, total_pages + 1)
        )
    else:
        left_middle_page = max(1, current_page - 2)
        right_middle_page = min(total_pages, current_page + 2)
        buttons.extend(
            [
                create_button("1", f"{base_prefix}1{suffix}"),
                InlineKeyboardButton(
                    text=middle_button,
                    callback_data=f"{base_prefix}{left_middle_page}{suffix}",
                ),
                create_button(
                    str(current_page), f"{base_prefix}{current_page}{suffix}", True
                ),
                InlineKeyboardButton(
                    text=middle_button,
                    callback_data=f"{base_prefix}{right_middle_page}{suffix}",
                ),
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

    elif buttons and buttons[0].text == left_arrow:
        buttons[1:] = page_buttons

    else:
        buttons[0:0] = page_buttons

    callback_dict = {
        "a": "back",
        "c": content_type,
        "p": current_page,
        "e": extra_arg,
    }

    callback_data = json.dumps(callback_dict, separators=(",", ":"))

    back_button = InlineKeyboardButton(text="↩️", callback_data=callback_data)

    keyboard = [
        buttons,
        [back_button],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_pagination_handler(content_type: str, render_content: Callable):
    async def handler(callback: CallbackQuery, language_code: str):
        if callback.data.startswith(f"{content_type}_page_"):
            parts = callback.data.split("_")
            page = int(parts[2])
            extra_arg = parts[3] if len(parts) > 3 else ""

            if extra_arg:
                result = await render_content(page, language_code, extra_arg)
                caption, image_url, total_pages, builder = result

            else:
                result = await render_content(page, language_code)
                caption, image_url, total_pages, builder = result

            pagination_keyboard = get_pagination_keyboard(
                page, total_pages, content_type, extra_arg
            )

            if image_url:
                await callback.message.edit_media(
                    InputMediaPhoto(media=image_url, caption=caption),
                    reply_markup=pagination_keyboard,
                )

            elif builder:
                for button in pagination_keyboard.inline_keyboard:
                    builder.row(*button)

                keyboard = builder.as_markup()
                await callback.message.edit_text(caption, reply_markup=keyboard)

            else:
                await callback.message.edit_text(
                    caption, reply_markup=pagination_keyboard
                )

        await callback.answer()

    return handler


def get_category_keyboard() -> InlineKeyboardMarkup:
    categories = [
        InlineKeyboardButton(text="Tech", callback_data="category_tech"),
        InlineKeyboardButton(text="Retail", callback_data="category_retail"),
        InlineKeyboardButton(text="Finance", callback_data="category_finance"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[categories])


company_handler = create_pagination_handler("user-company", render_company_content)
company_admin_handler = create_pagination_handler(
    "admin-company", render_company_content_for_admin
)
product_handler = create_pagination_handler("product", render_product_content)
country_handler = create_pagination_handler("admin-country", render_country_content)
