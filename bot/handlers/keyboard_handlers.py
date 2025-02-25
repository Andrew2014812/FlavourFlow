from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.common.services.text_service import text_service


def get_reply_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    for button in text_service.buttons.get(language, {}).values():
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_language_keyboard():
    builder = ReplyKeyboardBuilder()
    for button in text_service.language_buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_contact_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    contact_button_text = text_service.get_text("send_contact", language)
    builder.add(KeyboardButton(text=contact_button_text, request_contact=True))
    return builder.as_markup(resize_keyboard=True)
