from aiogram import F, Router, Dispatcher
from aiogram.types import Message

from bot.common.crud.api.user import update_user
from bot.common.crud.bot.user_info import get_user_info
from bot.common.utils import get_text
from bot.handlers.reply_buttons_handlers import handle_profile

router = Router()


@router.message(
    F.text.contains("Прізвище:") |
    F.text.contains("Ім'я:") |
    F.text.contains("First name:") |
    F.text.contains("Last name:")
)
async def process_profile_update(message: Message):
    language_code = get_user_info(message.from_user.id).language_code

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
            get_text("invalid_format", language_code)
        )
        return

    data_for_update = {field_mappings.get(k + ":", k): v for k, v in raw_dict.items() if v != ''}

    if not data_for_update:
        await message.answer(get_text("invalid_format", language_code))
        return

    await update_user(message.from_user.id, **data_for_update)

    await message.answer(
        get_text('profile_updated', language_code)
    )

    await handle_profile(message, language_code)


def register_profile_edit_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)