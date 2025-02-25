from aiogram import Router, Dispatcher, F as FILTER
from aiogram.types import Message

from bot.common.services.text_service import text_service
from bot.common.services.user_info_service import get_user_info
from bot.common.services.user_service import update_user
from bot.handlers.reply_buttons_handlers import handle_profile

router = Router()


@router.message(
    FILTER.text.contains("Прізвище:") |
    FILTER.text.contains("Ім'я:") |
    FILTER.text.contains("First name:") |
    FILTER.text.contains("Last name:")
)
async def process_profile_update(message: Message):
    user_info = await get_user_info(message.from_user.id)
    language_code = user_info.language_code

    lines = message.text.strip().split("\n")

    field_mappings = {
        "First name:": "first_name",
        "Last name:": "last_name",

        "Ім'я:": "first_name",
        "Прізвище:": "last_name",
    }

    try:
        raw_dict = dict(item.split(': ', 1) for item in lines if ': ' in item)
    except ValueError:
        await message.answer(
            text_service.get_text("invalid_format", language_code)
        )
        return

    data_for_update = {field_mappings.get(k + ":", k): v for k, v in raw_dict.items() if v != ''}

    if not data_for_update:
        await message.answer(text_service.get_text("invalid_format", language_code))
        return

    await update_user(message.from_user.id, **data_for_update)

    await message.answer(
        text_service.get_text('profile_updated', language_code)
    )

    await handle_profile(message, language_code)


def register_profile_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
