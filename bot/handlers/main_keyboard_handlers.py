import json

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from ..common.services.text_service import text_service
from ..common.services.user_service import get_user


async def get_main_keyboard(language_code: str, telegram_id: int):
    builder = ReplyKeyboardBuilder()
    buttons_dict = text_service.buttons.get(language_code, {}).copy()
    del buttons_dict["back"]

    result = await get_user(telegram_id)
    user_role = result.role

    if user_role == "user":
        del buttons_dict["admin_panel"]

    for button in buttons_dict.values():
        builder.add(KeyboardButton(text=button))

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_language_keyboard():
    builder = ReplyKeyboardBuilder()
    for button in text_service.language_buttons:
        builder.add(KeyboardButton(text=button))

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_contact_keyboard(language_code: str):
    builder = ReplyKeyboardBuilder()
    contact_button_text = text_service.get_text("send_contact", language_code)
    builder.add(KeyboardButton(text=contact_button_text, request_contact=True))
    return builder.as_markup(resize_keyboard=True)


def get_admin_panel_keyboard(language_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, button_text in text_service.admin_buttons.get(language_code, {}).items():
        callback_dict = {
            "t": key,
            "a": "nav",
            "p": 1,
        }

        callback_data = json.dumps(callback_dict, separators=(",", ":"))

        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    builder.adjust(2)

    return builder.as_markup()
