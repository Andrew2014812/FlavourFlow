from functools import wraps
from typing import Callable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.user.schemas import UserResponseMe
from bot.common.services.text_service import text_service
from bot.common.services.user_service import get_user
from bot.handlers.entity_handlers.main_handlers import show_main_menu
from bot.handlers.main_keyboard_handlers import get_admin_panel_keyboard
from bot.handlers.pagination_handlers import get_category_keyboard

button_handlers = {}


def register_button_handler(*button_texts):
    def decorator(func):
        for text in button_texts:
            button_handlers[text] = func
        return func

    return decorator


def admin_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(message: Message, language_code: str, *args, **kwargs):
        user_data: UserResponseMe = await get_user(message.from_user.id)

        if user_data.role != "admin":
            await message.answer(text_service.get_text("no_access", language_code))
            return

        return await func(message, language_code, *args, **kwargs)

    return wrapper


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
            ]
        ]
    )

    await message.answer(profile_text, reply_markup=keyboard)


@register_button_handler(
    text_service.buttons["en"]["restaurants"], text_service.buttons["ua"]["restaurants"]
)
async def handle_restaurants(message: Message, language_code: str):
    await message.answer(
        text=text_service.get_text("select_category", language_code),
        reply_markup=get_category_keyboard(),
    )


@register_button_handler(
    text_service.buttons["en"]["back"], text_service.buttons["ua"]["back"]
)
async def handle_back(message: Message, language_code: str):
    await show_main_menu(message, language_code)


@register_button_handler(
    text_service.buttons["en"]["admin_panel"], text_service.buttons["ua"]["admin_panel"]
)
@admin_required
async def handle_admin(message: Message, language_code: str):
    await message.answer(
        text_service.get_text("select_admin_action", language_code),
        reply_markup=get_admin_panel_keyboard(language_code),
    )
