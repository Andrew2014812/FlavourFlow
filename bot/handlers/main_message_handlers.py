from aiogram import Dispatcher
from aiogram import F as FILTER
from aiogram import Router
from aiogram.types import Message

from api.app.user.schemas import Token, UserCreate

from ..common.services.text_service import text_service
from ..common.services.user_info_service import (
    create_user_info,
    get_user_info,
    update_user_info,
)
from ..common.services.user_service import get_user, login_user, register_user
from ..handlers.entity_handlers.main_handlers import show_main_menu
from ..handlers.main_keyboard_handlers import get_contact_keyboard
from ..handlers.reply_buttons_handlers import button_handlers

router = Router()


@router.message(FILTER.text.in_(text_service.language_buttons))
async def handle_language_choice(message: Message):
    telegram_id = message.from_user.id
    language_code = "ua" if message.text == "🇺🇦 Українська" else "en"
    existing_user = await get_user(telegram_id)

    if existing_user:
        await update_user_info(telegram_id, language_code=language_code)
        await message.answer(text_service.get_text("settings_updated", language_code))
        await show_main_menu(message, language_code)

    else:
        await create_user_info(telegram_id, language_code)
        await message.answer(text_service.get_text("request_phone", language_code))
        await message.answer(
            text_service.get_text("share_contact", language_code),
            reply_markup=get_contact_keyboard(language_code),
        )


@router.message(FILTER.content_type == "contact")
async def handle_contact(message: Message):
    user_id = message.from_user.id
    user_info = await get_user_info(user_id)

    if not user_info.is_registered:
        user_create = UserCreate(
            first_name=message.contact.first_name,
            last_name=message.contact.last_name,
            phone_number=message.contact.phone_number,
            telegram_id=message.from_user.id,
        )
        user = await register_user(user_create)
        user_info = await update_user_info(
            user.telegram_id, is_registered=True, phone_number=user.phone_number
        )

    token: Token = await login_user(user_info)
    await update_user_info(
        user_info.telegram_id,
        access_token=token.access_token,
        token_type=token.token_type,
    )

    await message.answer(
        text_service.get_text("contact_received", user_info.language_code)
    )

    await show_main_menu(message, user_info.language_code)


@router.message()
async def handle_buttons(message: Message):
    telegram_id = message.from_user.id
    user_info = await get_user_info(telegram_id)
    language_code = user_info.language_code

    if message.text in text_service.buttons.get(language_code, {}).values():
        handler = button_handlers.get(message.text)
        if handler:
            await handler(message, language_code)
        else:
            await message.answer(text_service.get_text("unknown_option", language_code))
    else:
        await message.answer(text_service.get_text("use_buttons", language_code))


def register_main_message_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
