from aiogram import Dispatcher, Router
from aiogram.types import Message

from api.app.user.schemas import UserCreate

from ..common.services.gastronomy_service import kitchen_service
from ..common.services.text_service import text_service
from ..common.services.user_info_service import (
    create_user_info,
    get_user_info,
    update_user_info,
)
from ..common.services.user_service import login_user, register_user
from ..handlers.entity_handlers.main_handlers import show_main_menu
from ..handlers.main_keyboard_handlers import get_contact_keyboard
from ..handlers.pagination_handlers import send_paginated_message
from ..handlers.reply_buttons_handlers import button_handlers

router = Router()


@router.message(lambda msg: msg.text in text_service.language_buttons)
async def handle_language_choice(message: Message):
    telegram_id = message.from_user.id
    language_code = "ua" if message.text == "🇺🇦 Українська" else "en"
    user_info = await get_user_info(telegram_id)

    if user_info:
        await update_user_info(telegram_id, language_code=language_code)
        await message.answer(text_service.get_text("settings_updated", language_code))
        await show_main_menu(message, language_code)
    else:
        await create_user_info(telegram_id, language_code)
        await message.answer(
            text_service.get_text("request_phone", language_code),
            reply_markup=get_contact_keyboard(language_code),
        )


@router.message(lambda msg: msg.content_type == "contact")
async def handle_contact(message: Message):
    user_info = await get_user_info(message.from_user.id)
    if not user_info.is_registered:
        user_create = UserCreate(
            first_name=message.contact.first_name,
            last_name=message.contact.last_name,
            phone_number=message.contact.phone_number,
            telegram_id=message.from_user.id,
        )
        user = await register_user(user_create)
        await update_user_info(
            user.telegram_id, is_registered=True, phone_number=user.phone_number
        )

    token = await login_user(user_info)
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
    user_info = await get_user_info(message.from_user.id)
    language_code = user_info.language_code
    text = message.text

    kitchen_list = await kitchen_service.get_list(page=1)
    kitchen_titles = [
        kitchen.title_en if language_code == "en" else kitchen.title_ua
        for kitchen in kitchen_list.kitchens
    ]

    if text in kitchen_titles:
        kitchen = next(
            k
            for k in kitchen_list.kitchens
            if (language_code == "en" and k.title_en == text)
            or (language_code == "ua" and k.title_ua == text)
        )
        await send_paginated_message(
            message, "user-company", 1, language_code, str(kitchen.id)
        )
        return

    if text in text_service.buttons.get(language_code, {}).values():
        handler = button_handlers.get(text)
        if handler:
            await handler(message, language_code)
        else:
            await message.answer(text_service.get_text("unknown_option", language_code))
    else:
        await message.answer(text_service.get_text("use_buttons", language_code))


def register_main_message_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
