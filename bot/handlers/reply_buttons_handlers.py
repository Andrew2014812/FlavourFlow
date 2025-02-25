from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from api.app.user.schemas import UserResponseMe
from bot.common.services.api.user_service import get_user
from bot.config import buttons
from bot.handlers.command_handlers import get_text

button_handlers = {}


def register_button_handler(*button_texts):
    def decorator(func):
        for text in button_texts:
            button_handlers[text] = func
        return func

    return decorator


@register_button_handler("Настройк")
async def handle_settings(message: Message, language: str):
    await message.answer(get_text("settings_message", language))


@register_button_handler(buttons["en"]["profile"], buttons["ua"]["profile"])
async def handle_profile(message: Message, language_code: str):
    user_data: UserResponseMe = await get_user(message.from_user.id)

    last_name = user_data.last_name if user_data.last_name else ""
    profile_data = {
        "name": f'{user_data.first_name} {last_name}',
        "language": "Українська" if language_code == "ua" else "English",
        "bonuses": user_data.bonuses,
        "phone": user_data.phone_number
    }

    profile_text = get_text("profile_message", language_code).format(**profile_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('profile_edit', language_code), callback_data="edit_profile")]
    ])

    await message.answer(profile_text, reply_markup=keyboard)


@register_button_handler("Помощь")
async def handle_help(message: Message, language: str):
    await message.answer(get_text("help_message", language))
