from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.common.utils import get_text
from bot.config import buttons, language_buttons


def get_reply_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    for button in buttons.get(language, {}).values():
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_language_keyboard():
    builder = ReplyKeyboardBuilder()
    for button in language_buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_contact_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    contact_button_text = get_text("send_contact", language)
    builder.add(KeyboardButton(text=contact_button_text, request_contact=True))
    return builder.as_markup(resize_keyboard=True)
