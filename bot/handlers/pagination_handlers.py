import json
from typing import Callable, List, Optional, Tuple

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..handlers.entity_handlers.company_handlers import (
    company_handler as company_entity_handler,
)
from ..handlers.entity_handlers.company_handlers import render_company_content
from ..handlers.entity_handlers.gastronomy_handlers import (
    country_handler as country_gastronomy_handler,
)
from ..handlers.entity_handlers.gastronomy_handlers import (
    kitchen_handler as kitchen_gastronomy_handler,
)
from ..handlers.entity_handlers.product_handlers import render_product_content

ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"
DOT_MIDDLE = "🔘"
ARROW_BACK = "↩️"


class PaginationConfig:
    def __init__(
        self,
        content_type: str,
        render_content: Callable,
        items_per_row: int = 2,
        show_page_numbers: bool = True,
    ):
        self.content_type = content_type
        self.render_content = render_content
        self.items_per_row = items_per_row
        self.show_page_numbers = show_page_numbers


class PaginationBuilder:
    @staticmethod
    def create_button(
        text: str,
        callback_data: str,
        is_current: bool = False,
    ) -> InlineKeyboardButton:
        display_text = f"[{text}]" if is_current else text
        return InlineKeyboardButton(text=display_text, callback_data=callback_data)

    @staticmethod
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

    @staticmethod
    def get_navigation_buttons(
        current_page: int,
        total_pages: int,
        content_type: str,
        extra_arg: str = "",
    ) -> List[InlineKeyboardButton]:
        buttons = []

        if current_page > 1:
            prev_data = PaginationBuilder.make_callback_data(
                content_type, "nav", current_page - 1, extra_arg
            )
            buttons.append(PaginationBuilder.create_button(ARROW_LEFT, prev_data))

        if current_page < total_pages:
            next_data = PaginationBuilder.make_callback_data(
                content_type, "nav", current_page + 1, extra_arg
            )
            buttons.append(PaginationBuilder.create_button(ARROW_RIGHT, next_data))

        return buttons

    @staticmethod
    def get_page_buttons(
        current_page: int,
        total_pages: int,
        content_type: str,
        extra_arg: str = "",
    ) -> List[InlineKeyboardButton]:
        if total_pages <= 5:
            return [
                PaginationBuilder.create_button(
                    str(page),
                    PaginationBuilder.make_callback_data(
                        content_type, "nav", page, extra_arg
                    ),
                    page == current_page,
                )
                for page in range(1, total_pages + 1)
            ]

        middle_page = total_pages // 2

        if current_page <= 3:
            return [
                *[
                    PaginationBuilder.create_button(
                        str(page),
                        PaginationBuilder.make_callback_data(
                            content_type, "nav", page, extra_arg
                        ),
                        page == current_page,
                    )
                    for page in range(1, 4)
                ],
                PaginationBuilder.create_button(
                    DOT_MIDDLE,
                    PaginationBuilder.make_callback_data(
                        content_type, "nav", middle_page, extra_arg
                    ),
                ),
                *[
                    PaginationBuilder.create_button(
                        str(page),
                        PaginationBuilder.make_callback_data(
                            content_type, "nav", page, extra_arg
                        ),
                    )
                    for page in [total_pages - 1, total_pages]
                ],
            ]

        if current_page >= total_pages - 2:
            return [
                PaginationBuilder.create_button(
                    "1",
                    PaginationBuilder.make_callback_data(
                        content_type, "nav", 1, extra_arg
                    ),
                ),
                PaginationBuilder.create_button(
                    DOT_MIDDLE,
                    PaginationBuilder.make_callback_data(
                        content_type, "nav", middle_page, extra_arg
                    ),
                ),
                *[
                    PaginationBuilder.create_button(
                        str(page),
                        PaginationBuilder.make_callback_data(
                            content_type, "nav", page, extra_arg
                        ),
                        page == current_page,
                    )
                    for page in range(total_pages - 2, total_pages + 1)
                ],
            ]

        return [
            PaginationBuilder.create_button(
                "1",
                PaginationBuilder.make_callback_data(content_type, "nav", 1, extra_arg),
            ),
            PaginationBuilder.create_button(
                DOT_MIDDLE,
                PaginationBuilder.make_callback_data(
                    content_type, "nav", current_page - 2, extra_arg
                ),
            ),
            PaginationBuilder.create_button(
                str(current_page),
                PaginationBuilder.make_callback_data(
                    content_type, "nav", current_page, extra_arg
                ),
                True,
            ),
            PaginationBuilder.create_button(
                DOT_MIDDLE,
                PaginationBuilder.make_callback_data(
                    content_type, "nav", current_page + 2, extra_arg
                ),
            ),
            PaginationBuilder.create_button(
                str(total_pages),
                PaginationBuilder.make_callback_data(
                    content_type, "nav", total_pages, extra_arg
                ),
            ),
        ]

    @staticmethod
    def build_pagination_keyboard(
        current_page: int,
        total_pages: int,
        content_type: str,
        extra_arg: str = "",
    ) -> InlineKeyboardMarkup:
        nav_buttons = PaginationBuilder.get_navigation_buttons(
            current_page, total_pages, content_type, extra_arg
        )

        page_buttons = PaginationBuilder.get_page_buttons(
            current_page, total_pages, content_type, extra_arg
        )

        if len(nav_buttons) == 2:
            buttons = [nav_buttons[0], *page_buttons, nav_buttons[1]]

        elif nav_buttons and nav_buttons[0].text == ARROW_LEFT:
            buttons = [nav_buttons[0], *page_buttons]

        else:
            buttons = [*page_buttons, *nav_buttons]

        back_data = PaginationBuilder.make_callback_data(
            content_type, "back", current_page, extra_arg
        )
        back_button = PaginationBuilder.create_button(ARROW_BACK, back_data)

        return InlineKeyboardMarkup(inline_keyboard=[buttons, [back_button]])


class PaginationHandler:
    @staticmethod
    async def update_paginated_message(
        callback: CallbackQuery,
        content_type: str,
        page: int,
        language_code: str,
        extra_arg: str = "",
        make_send: bool = False,
    ) -> None:
        content_result = await PaginationHandler.get_content(
            content_type, page, language_code, extra_arg
        )

        if not content_result:
            await callback.answer("Content not available")
            return

        caption, image_url, total_pages, builder = content_result

        keyboard = PaginationBuilder.build_pagination_keyboard(
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

            if make_send:
                await callback.message.answer(caption, reply_markup=builder.as_markup())
            else:
                await callback.message.edit_text(
                    caption, reply_markup=builder.as_markup()
                )
        else:
            await callback.message.edit_text(caption, reply_markup=keyboard)

    @staticmethod
    async def get_content(
        content_type: str,
        page: int,
        language_code: str,
        extra_arg: str = "",
    ) -> Optional[Tuple[str, Optional[str], int, Optional[InlineKeyboardBuilder]]]:
        handlers = {
            "user-company": render_company_content,
            "admin-company": company_entity_handler.render_admin_list_content,
            "product": render_product_content,
            "admin-country": country_gastronomy_handler.render_admin_list_content,
            "admin-kitchen": kitchen_gastronomy_handler.render_admin_list_content,
        }

        if handler := handlers.get(content_type):
            if extra_arg:
                return await handler(page, language_code, extra_arg)
            return await handler(page, language_code)
        return None

    @staticmethod
    def create_handler(config: PaginationConfig) -> Callable:

        async def handler(callback: CallbackQuery, language_code: str, **kwargs):
            data = json.loads(callback.data)

            if data.get("t") != config.content_type or data.get("a") not in [
                "nav",
                "back",
            ]:
                return

            if data["a"] == "nav":
                await PaginationHandler.update_paginated_message(
                    callback,
                    config.content_type,
                    data["p"],
                    language_code,
                    data.get("e", ""),
                    kwargs.get("make_send", False),
                )

            await callback.answer()

        return handler


def create_pagination_handler(content_type: str, render_content: Callable):
    return PaginationHandler.create_handler(
        PaginationConfig(content_type, render_content)
    )


company_handler = PaginationHandler.create_handler(
    PaginationConfig("user-company", render_company_content)
)

company_admin_handler = PaginationHandler.create_handler(
    PaginationConfig("admin-company", company_entity_handler.render_admin_list_content)
)

product_handler = PaginationHandler.create_handler(
    PaginationConfig("product", render_product_content)
)

country_handler = PaginationHandler.create_handler(
    PaginationConfig(
        "admin-country", country_gastronomy_handler.render_admin_list_content
    )
)

kitchen_handler = PaginationHandler.create_handler(
    PaginationConfig(
        "admin-kitchen", kitchen_gastronomy_handler.render_admin_list_content
    )
)


def get_category_keyboard() -> InlineKeyboardMarkup:
    categories = [
        {"text": "Tech", "value": "tech"},
        {"text": "Retail", "value": "retail"},
        {"text": "Finance", "value": "finance"},
    ]

    buttons = [
        PaginationBuilder.create_button(
            category["text"],
            json.dumps(
                {"t": "category", "v": category["value"]}, separators=(",", ":")
            ),
        )
        for category in categories
    ]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
