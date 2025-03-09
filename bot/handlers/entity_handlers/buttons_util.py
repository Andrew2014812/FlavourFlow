from typing import Dict

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_admin_buttons(
    names: Dict[int, str], content_type: str, language_code: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    names_items = list(names.items())

    for i in range(0, len(names_items), 2):
        button_title = names_items[i][1]
        button_item_id = names_items[i][0]

        row_buttons = [
            InlineKeyboardButton(
                text=button_title,
                callback_data=f"{content_type}_{button_item_id}",
            )
        ]

        if i + 1 < len(names_items):
            button_title = names_items[i + 1][1]
            button_item_id = names_items[i + 1][0]

            row_buttons.append(
                InlineKeyboardButton(
                    text=button_title,
                    callback_data=f"{content_type}_{button_item_id}",
                )
            )

        builder.row(*row_buttons)

    add_button_text = "🆕 Додати" if language_code == "ua" else "🆕 Add"
    builder.row(
        InlineKeyboardButton(text=add_button_text, callback_data=f"add_{content_type}")
    )

    return builder
