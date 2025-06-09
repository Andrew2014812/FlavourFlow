import json
from enum import Enum
from typing import Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...common.services.text_service import text_service


class ActionType(Enum):
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"


async def build_admin_buttons(
    names: Dict[int, str],
    content_type: str,
    language_code: str,
    page: int,
    extra_arg: str = "",
):
    builder = InlineKeyboardBuilder()
    items = list(names.items())

    for i in range(0, len(items), 2):
        buttons = []
        item_id, title = items[i]
        callback_data = json.dumps(
            {"t": content_type, "id": item_id, "a": "details", "p": page},
            separators=(",", ":"),
        )
        buttons.append(InlineKeyboardButton(text=title, callback_data=callback_data))

        if i + 1 < len(items):
            item_id, title = items[i + 1]
            callback_data = json.dumps(
                {"t": content_type, "id": item_id, "a": "details", "p": page},
                separators=(",", ":"),
            )
            buttons.append(
                InlineKeyboardButton(text=title, callback_data=callback_data)
            )

        builder.row(*buttons)

    add_text = "🆕 Додати" if language_code == "ua" else "🆕 Add"
    callback_data = {"a": "add", "t": content_type, "p": page}
    if extra_arg:
        callback_data["e"] = extra_arg
    builder.row(
        InlineKeyboardButton(
            text=add_text,
            callback_data=json.dumps(callback_data, separators=(",", ":")),
        )
    )
    return builder


async def convert_raw_text_to_valid_dict(
    raw_text: str, field_mapping: Dict, is_allow_empty: bool = False
):
    items = (
        raw_text.strip().split("; ")
        if "; " in raw_text
        else raw_text.strip().split(";")
    )
    try:
        raw_dict = dict(item.split(": ", 1) for item in items if ": " in item)
        data = {field_mapping.get(k + ":", k): v for k, v in raw_dict.items() if v}

        if not data:
            return {"error": "invalid_format"}

        if not is_allow_empty and not any(
            key in data for key in ["title_ua", "title_en"]
        ):
            return {"error": "invalid_format"}

        return data
    except ValueError:
        return {"error": "invalid_format"}


def get_item_admin_details_keyboard(
    content_type: str, page: int, language_code: str, item_id: int
):
    builder = InlineKeyboardBuilder()
    buttons = [
        ("edit", "edit_button", "Змінити" if language_code == "ua" else "Edit"),
        ("delete", "delete_button", "Видалити" if language_code == "ua" else "Delete"),
    ]

    if content_type == "admin-company":
        buttons.append(
            (
                "products",
                "products_button",
                "Продукти" if language_code == "ua" else "Products",
            )
        )

    for action, text_key, button_text in buttons:
        callback_data = json.dumps(
            {"t": content_type, "p": page, "a": action, "id": item_id},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    callback_data = json.dumps(
        {"t": f"{content_type}-details", "p": page, "a": "back"},
        separators=(",", ":"),
    )
    builder.add(
        InlineKeyboardButton(
            text=text_service.get_text("back_button", language_code),
            callback_data=callback_data,
        )
    )

    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard(language_code: str, content_type: str, page: int):
    cancel_text = text_service.get_text("cancel", language_code)
    callback_data = json.dumps(
        {"t": content_type, "a": "cancel", "p": page}, separators=(",", ":")
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cancel_text, callback_data=callback_data)]
        ]
    )


def get_confirm_keyboard(
    language_code: str, content_type: str, page: int, item_id: int
):
    cancel = get_cancel_keyboard(language_code, content_type, page)
    confirm_text = "Підтвердити" if language_code == "ua" else "Confirm"
    confirm_data = json.dumps(
        {"a": "confirm_delete", "t": content_type, "p": page, "id": item_id},
        separators=(",", ":"),
    )
    cancel.inline_keyboard[0].append(
        InlineKeyboardButton(text=confirm_text, callback_data=confirm_data)
    )
    return cancel
