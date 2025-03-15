import json
from typing import Callable, List

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from ..handlers.entity_handlers.company_handlers import (
    render_company_content,
    render_company_content_for_admin,
)
from ..handlers.entity_handlers.product_handlers import render_product_content
from .entity_handlers.gastronomy_handlers import render_country_content

LEFT_ARROW = "⬅️"
RIGHT_ARROW = "➡️"
MIDDLE_DOT = "🔘"
BACK_ARROW = "↩️"


def create_button(
    text: str,
    callback_data: str,
    is_current: bool = False,
) -> InlineKeyboardButton:
    display_text = f"[{text}]" if is_current else text
    return InlineKeyboardButton(text=display_text, callback_data=callback_data)


def make_callback_data(
    content_type: str,
    action: str,
    page: int,
    extra_arg: str = "",
) -> str:
    data = {"t": content_type, "a": action, "p": page}

    if extra_arg:
        data["e"] = extra_arg

    return json.dumps(data, separators=(",", ":"))


def get_navigation_buttons(
    current_page: int,
    total_pages: int,
    content_type: str,
    extra_arg: str = "",
) -> List[InlineKeyboardButton]:
    buttons = []

    if current_page > 1:
        prev_page_data = make_callback_data(
            content_type, "nav", current_page - 1, extra_arg
        )

        buttons.append(create_button(text=LEFT_ARROW, callback_data=prev_page_data))

    if current_page < total_pages:
        next_page_data = make_callback_data(
            content_type, "nav", current_page + 1, extra_arg
        )

        buttons.append(create_button(text=RIGHT_ARROW, callback_data=next_page_data))

    return buttons


def get_page_buttons(
    current_page: int,
    total_pages: int,
    content_type: str,
    extra_arg: str = "",
) -> List[InlineKeyboardButton]:
    buttons = []

    if total_pages <= 5:
        for page in range(1, total_pages + 1):
            callback = make_callback_data(content_type, "nav", page, extra_arg)
            buttons.append(
                create_button(
                    text=str(page),
                    callback_data=callback,
                    is_current=page == current_page,
                )
            )

        return buttons

    if current_page <= 3:
        buttons = [
            create_button(
                text=str(i),
                callback_data=make_callback_data(content_type, "nav", i, extra_arg),
                is_current=i == current_page,
            )
            for i in range(1, 4)
        ]

        middle_page = total_pages // 2
        buttons.extend(
            [
                create_button(
                    text=MIDDLE_DOT,
                    callback_data=make_callback_data(
                        content_type, "nav", middle_page, extra_arg
                    ),
                ),
                create_button(
                    text=str(total_pages - 1),
                    callback_data=make_callback_data(
                        content_type, "nav", total_pages - 1, extra_arg
                    ),
                ),
                create_button(
                    text=str(total_pages),
                    callback_data=make_callback_data(
                        content_type, "nav", total_pages, extra_arg
                    ),
                ),
            ]
        )

        return buttons

    if current_page >= total_pages - 2:
        middle_page = total_pages // 2

        buttons = [
            create_button(
                text="1",
                callback_data=make_callback_data(content_type, "nav", 1, extra_arg),
            ),
            create_button(
                text=MIDDLE_DOT,
                callback_data=make_callback_data(
                    content_type, "nav", middle_page, extra_arg
                ),
            ),
        ]

        buttons.extend(
            [
                create_button(
                    text=str(i),
                    callback_data=make_callback_data(content_type, "nav", i, extra_arg),
                    is_current=i == current_page,
                )
                for i in range(total_pages - 2, total_pages + 1)
            ]
        )

        return buttons

    left_middle = max(1, current_page - 2)
    right_middle = min(total_pages, current_page + 2)

    buttons = [
        create_button(
            text="1",
            callback_data=make_callback_data(content_type, "nav", 1, extra_arg),
        ),
        create_button(
            text=MIDDLE_DOT,
            callback_data=make_callback_data(
                content_type, "nav", left_middle, extra_arg
            ),
        ),
        create_button(
            text=str(current_page),
            callback_data=make_callback_data(
                content_type, "nav", current_page, extra_arg
            ),
            is_current=True,
        ),
        create_button(
            text=MIDDLE_DOT,
            callback_data=make_callback_data(
                content_type, "nav", right_middle, extra_arg
            ),
        ),
        create_button(
            text=str(total_pages),
            callback_data=make_callback_data(
                content_type, "nav", total_pages, extra_arg
            ),
        ),
    ]

    return buttons


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    content_type: str,
    extra_arg: str = "",
) -> InlineKeyboardMarkup:
    nav_buttons = get_navigation_buttons(
        current_page,
        total_pages,
        content_type,
        extra_arg,
    )
    page_buttons = get_page_buttons(
        current_page,
        total_pages,
        content_type,
        extra_arg,
    )

    if len(nav_buttons) == 2:
        buttons = [nav_buttons[0], *page_buttons, nav_buttons[1]]

    elif len(nav_buttons) == 1 and nav_buttons[0].text == LEFT_ARROW:
        buttons = [nav_buttons[0], *page_buttons]

    else:
        buttons = [*page_buttons, *nav_buttons]

    back_data = make_callback_data(content_type, "back", current_page, extra_arg)
    back_button = create_button(text=BACK_ARROW, callback_data=back_data)

    return InlineKeyboardMarkup(inline_keyboard=[buttons, [back_button]])


def create_pagination_handler(content_type: str, render_content: Callable):
    async def handler(callback: CallbackQuery, language_code: str):
        data = json.loads(callback.data)

        if data.get("t") != content_type or data.get("a") not in ["nav", "back"]:
            return

        if data["a"] == "nav":
            page = data["p"]
            extra_arg = data.get("e", "")

            result = await (
                render_content(page, language_code, extra_arg)
                if extra_arg
                else render_content(page, language_code)
            )

            caption, image_url, total_pages, builder = result
            keyboard = get_pagination_keyboard(
                page, total_pages, content_type, extra_arg
            )

            if image_url:
                await callback.message.edit_media(
                    InputMediaPhoto(media=image_url, caption=caption),
                    reply_markup=keyboard,
                )

            elif builder:
                for row in keyboard.inline_keyboard:
                    builder.row(*row)

                await callback.message.edit_text(
                    caption, reply_markup=builder.as_markup()
                )

            else:
                await callback.message.edit_text(caption, reply_markup=keyboard)

        await callback.answer()

    return handler


def get_category_keyboard() -> InlineKeyboardMarkup:
    category_data = [
        {"text": "Tech", "value": "tech"},
        {"text": "Retail", "value": "retail"},
        {"text": "Finance", "value": "finance"},
    ]

    buttons = [
        create_button(
            text=category["text"],
            callback_data=json.dumps(
                {"t": "category", "v": category["value"]}, separators=(",", ":")
            ),
        )
        for category in category_data
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


company_handler = create_pagination_handler("user-company", render_company_content)
company_admin_handler = create_pagination_handler(
    "admin-company", render_company_content_for_admin
)
product_handler = create_pagination_handler("product", render_product_content)
country_handler = create_pagination_handler("admin-country", render_country_content)
