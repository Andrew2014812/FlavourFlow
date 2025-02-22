from aiogram import F, Router, Dispatcher
from aiogram.types import Message

from api.app.user.schemas import UserCreate
from bot.common.api_crud import register_user, login_user
from bot.common.bot_crud import create_user_info, get_user_info, update_user_info
from bot.common.utils import get_text
from bot.config import language_buttons, buttons
from bot.handlers.button_handlers import button_handlers
from bot.handlers.display_handlers import get_contact_keyboard, get_reply_keyboard

router = Router()


@router.message(F.text.in_(language_buttons))
async def handle_language_choice(message: Message):
    telegram_id = message.from_user.id
    language_code = "ua" if message.text == "🇺🇦 Українська" else "en"
    create_user_info(telegram_id, language_code)

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
    user_info = get_user_info(user_id)

    if not user_info.is_registered:
        user_create = UserCreate(
            first_name=message.contact.first_name,
            last_name=message.contact.last_name,
            phone_number=message.contact.phone_number,
            telegram_id=message.from_user.id
        )

        user = await register_user(user_create)
        user_info = update_user_info(user.telegram_id, is_registered=True, phone_number=user.phone_number)

    token = await login_user(user_info)
    update_user_info(user_info.telegram_id, access_token=token.access_token, token_type=token.token_type)
    message_text = "contact_received"

    await message.answer(
        get_text(message_text, user_info.language_code),
        reply_markup=get_reply_keyboard(user_info.language_code)
    )


@router.message()
async def handle_buttons(message: Message):
    telegram_id = message.from_user.id
    language_code = get_user_info(telegram_id).language_code

    if message.text in buttons.get(language_code, {}).values():

        handler = button_handlers.get(message.text)

        if handler:
            await handler(message, language_code)

        else:
            await message.answer(get_text("unknown_option", language_code))
    else:
        await message.answer(get_text("use_buttons", language_code))


def register_message_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
