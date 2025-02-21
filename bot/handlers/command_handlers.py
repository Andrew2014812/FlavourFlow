from aiogram import Router, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from api.app.user.schemas import UserCreate
from bot.common.crud import register_user
from bot.common.utils import get_text, load_texts_from_json
from bot.config import texts_json_path
from bot.handlers.button_handlers import button_handlers

router = Router()

user_languages = {}

buttons, language_buttons = load_texts_from_json(texts_json_path)


def get_reply_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    for button in buttons.get(language, {}).values():
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_language_keyboard():
    builder = ReplyKeyboardBuilder()
    print(language_buttons)
    for button in language_buttons:
        builder.add(KeyboardButton(text=button))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_contact_keyboard(language: str):
    builder = ReplyKeyboardBuilder()
    contact_button_text = get_text("send_contact", language)
    builder.add(KeyboardButton(text=contact_button_text, request_contact=True))
    return builder.as_markup(resize_keyboard=True)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        get_text("select_language", "ua"),
        reply_markup=get_language_keyboard()
    )


@router.message(F.text.in_(language_buttons))
async def handle_language_choice(message: Message):
    user_id = message.from_user.id
    language_code = "ua" if message.text == "🇺🇦 Українська" else "en"
    user_languages[user_id] = language_code

    await message.answer(
        get_text("request_phone", language_code)
    )

    await message.answer(
        get_text("share_contact", language_code),
        reply_markup=get_contact_keyboard(language_code)
    )


@router.message(F.content_type == "contact")
async def handle_contact(message: Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "ua")

    user_create = UserCreate(
        first_name=message.contact.first_name,
        last_name=message.contact.last_name,
        phone_number=message.contact.phone_number,
        telegram_id=message.from_user.id
    )

    result = await register_user(user_create)

    if result:
        message_text = "contact_received"
    else:
        message_text = "contact_already_registered"

    await message.answer(
        get_text(message_text, language),
        reply_markup=get_reply_keyboard(language)
    )


@router.message()
async def handle_buttons(message: Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "ua")

    if message.text in buttons.get(language, {}).values():

        handler = button_handlers.get(message.text)
        if handler:

            await handler(message, language)
        else:
            await message.answer(get_text("unknown_option", language))
    else:
        await message.answer(get_text("use_buttons", language))


def register_command_handler(dp: Dispatcher):
    dp.include_router(router)
