from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.user.schemas import UserResponseMe
from bot.common.services.text_service import text_service
from bot.common.services.user_service import get_user

button_handlers = {}


def register_button_handler(*button_texts):
    def decorator(func):
        for text in button_texts:
            button_handlers[text] = func
        return func

    return decorator


@register_button_handler("Настройк")
async def handle_settings(message: Message, language: str):
    await message.answer(text_service.get_text("settings_message", language))


@register_button_handler(
    text_service.buttons["en"]["profile"], text_service.buttons["ua"]["profile"]
)
async def handle_profile(message: Message, language_code: str):
    user_data: UserResponseMe = await get_user(message.from_user.id)

    last_name = user_data.last_name if user_data.last_name else ""
    profile_data = {
        "name": f"{user_data.first_name} {last_name}",
        "language": "Українська" if language_code == "ua" else "English",
        "bonuses": user_data.bonuses,
        "phone": user_data.phone_number,
    }

    profile_text = text_service.get_text("profile_message", language_code).format(
        **profile_data
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text_service.get_text("profile_edit", language_code),
                    callback_data="edit_profile",
                ),
                InlineKeyboardButton(
                    text="Test company pagination",
                    callback_data="company_page_1",
                ),
                InlineKeyboardButton(
                    text="Test product pagination",
                    callback_data="product_page_1",
                ),
            ]
        ]
    )

    await message.answer(profile_text, reply_markup=keyboard)


@register_button_handler("Помощь")
async def handle_help(message: Message, language: str):
    await message.answer(text_service.get_text("help_message", language))
