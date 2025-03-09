import json
from typing import Dict

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def build_admin_buttons(
    names: Dict[int, str],
    content_type: str,
    language_code: str,
    page: int,
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    names_items = list(names.items())

    for i in range(0, len(names_items), 2):
        button_title = names_items[i][1]
        button_item_id = names_items[i][0]
        callback_data_first = json.dumps(
            {"t": content_type, "id": button_item_id}, separators=(",", ":")
        )

        row_buttons = [
            InlineKeyboardButton(
                text=button_title,
                callback_data=callback_data_first,
            )
        ]

        if i + 1 < len(names_items):
            button_title = names_items[i + 1][1]
            button_item_id = names_items[i + 1][0]
            callback_data_second = json.dumps(
                {"t": content_type, "id": button_item_id}, separators=(",", ":")
            )

            row_buttons.append(
                InlineKeyboardButton(
                    text=button_title,
                    callback_data=callback_data_second,
                )
            )

        builder.row(*row_buttons)

    add_button_text = "🆕 Додати" if language_code == "ua" else "🆕 Add"
    add_callback_data = json.dumps(
        {"a": "add", "t": content_type, "p": page}, separators=(",", ":")
    )

    builder.row(
        InlineKeyboardButton(
            text=add_button_text,
            callback_data=add_callback_data,
        )
    )

    return builder


async def convert_raw_text_to_valid_dict(
    raw_text: str,
    field_mapping: Dict,
) -> Dict[str, str]:
    if "; " in raw_text:
        items = raw_text.strip().split("; ")

    else:
        items = raw_text.strip().split(";")

    try:
        raw_dict = dict(item.split(": ", 1) for item in items if ": " in item)

    except ValueError:
        return {"error": "invalid_format"}

    data_for_update = {
        field_mapping.get(k + ":", k): v for k, v in raw_dict.items() if v != ""
    }

    if not data_for_update:
        return {"error": "invalid_format"}

    valid_keys = set(field_mapping.values())

    if not valid_keys.issubset(set(data_for_update.keys())):
        return {"error": "invalid_format"}

    return data_for_update
