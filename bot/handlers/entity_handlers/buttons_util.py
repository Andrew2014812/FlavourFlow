from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_admin_buttons(
    names: List[str], content_type: str, page: int, language_code: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for i in range(0, len(names), 2):
        row_buttons = [
            InlineKeyboardButton(
                text=names[i],
                callback_data=f"{content_type}_{names[i].lower()}_page_{page}",
            )
        ]

        if i + 1 < len(names):
            row_buttons.append(
                InlineKeyboardButton(
                    text=names[i + 1],
                    callback_data=f"{content_type}_{names[i + 1].lower()}_page_{page}",
                )
            )

        builder.row(*row_buttons)

    add_button_text = "Додати" if language_code == "ua" else "Add"
    builder.row(
        InlineKeyboardButton(
            text=add_button_text, callback_data=f"{content_type}_add_page_{page}"
        )
    )

    return builder
