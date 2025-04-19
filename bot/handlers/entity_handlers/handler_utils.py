import json
from enum import Enum
from typing import Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.common.services.text_service import text_service


class ActionType(Enum):
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"


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
            {"t": content_type, "id": button_item_id, "a": "details", "p": page},
            separators=(",", ":"),
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
                {"t": content_type, "id": button_item_id, "a": "details", "p": page},
                separators=(",", ":"),
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
    is_allow_empty: bool = False,
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

    if not is_allow_empty and not valid_keys.issubset(set(data_for_update.keys())):
        return {"error": "invalid_format"}

    return data_for_update


def get_item_admin_details_keyboard(
    content_type: str,
    current_page: int,
    language_code: str,
    item_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, button_text in text_service.admin_actions.get(language_code, {}).items():
        callback_dict = {
            "t": content_type,
            "id": item_id,
            "a": key.lower(),
            "p": current_page,
        }

        callback_data = json.dumps(callback_dict, separators=(",", ":"))

        builder.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data,
            )
        )

    builder.adjust(2)
    back_data = json.dumps(
        {"t": f"{content_type}-details", "a": "back", "p": current_page},
        separators=(",", ":"),
    )

    builder.row(
        InlineKeyboardButton(
            text="↩️",
            callback_data=back_data,
        )
    )

    return builder.as_markup()


def get_cancel_keyboard(
    language_code: str,
    content_type: str,
    page: int,
) -> InlineKeyboardMarkup:
    cancel_text = text_service.get_text("cancel", language_code)
    callback_data = json.dumps(
        {"t": content_type, "a": "cancel", "p": page}, separators=(",", ":")
    )

    button = InlineKeyboardButton(text=cancel_text, callback_data=callback_data)
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


def get_confirm_keyboard(
    language_code: str, content_type: str, page: int, country_id: int
) -> InlineKeyboardMarkup:
    cancel = get_cancel_keyboard(language_code, content_type, page)
    confirm_text = "Підтвердити" if language_code == "ua" else "Confirm"

    confirm_data = json.dumps(
        {"a": "confirm_delete", "t": content_type, "p": page, "id": country_id},
        separators=(",", ":"),
    )

    cancel.inline_keyboard[0].append(
        InlineKeyboardButton(text=confirm_text, callback_data=confirm_data)
    )
    return cancel
