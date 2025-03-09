from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_item_buttons(
    names: List[str], content_type: str, page: int
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

    builder.row(
        InlineKeyboardButton(
            text="Добавить", callback_data=f"{content_type}_add_page_{page}"
        )
    )

    return builder
