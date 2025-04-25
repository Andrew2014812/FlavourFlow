import json

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from ..common.services.text_service import text_service
from ..common.services.user_service import get_user


async def get_main_keyboard(language_code: str, telegram_id: int):
    builder = ReplyKeyboardBuilder()
    buttons = text_service.buttons.get(language_code, {}).copy()
    buttons.pop("back", None)

    user = await get_user(telegram_id)
    if user and user.role == "user":
        buttons.pop("admin_panel", None)

    for button in buttons.values():
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
    builder.add(
        KeyboardButton(
            text=text_service.get_text("send_contact", language_code),
            request_contact=True,
        )
    )
    return builder.as_markup(resize_keyboard=True)


def get_admin_panel_keyboard(language_code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, text in text_service.admin_buttons.get(language_code, {}).items():
        callback_data = json.dumps(
            {"t": key, "a": "nav", "p": 1}, separators=(",", ":")
        )
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.adjust(2)
    return builder.as_markup()
