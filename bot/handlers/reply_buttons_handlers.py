from functools import wraps
from typing import Callable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.user.schemas import UserResponseMe

from ..common.services.gastronomy_service import kitchen_service
from ..common.services.text_service import text_service
from ..common.services.user_service import get_user
from ..handlers.entity_handlers.main_handlers import show_main_menu
from ..handlers.main_keyboard_handlers import get_admin_panel_keyboard
from ..handlers.pagination_handlers import PaginationHandler, get_category_keyboard

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

        if not user_data:
            user_data: UserResponseMe = await get_user(kwargs["telegram_id"])

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
        reply_markup=await get_category_keyboard(language_code),
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
async def handle_admin(message: Message, language_code: str, **kwargs):
    text = text_service.get_text("select_admin_action", language_code)
    reply_markup = get_admin_panel_keyboard(language_code)

    if kwargs.get("telegram_id"):
        await message.edit_text(text, reply_markup=reply_markup)

    else:
        await message.answer(text, reply_markup=reply_markup)


async def handle_kitchen_selection(message: Message, language_code: str):
    selected_kitchen_title = message.text

    kitchen_list = await kitchen_service.get_list(page=1)
    if not kitchen_list or not kitchen_list.kitchens:
        await message.answer(
            text_service.get_text("no_categories_available", language_code)
        )
        return

    selected_kitchen = next(
        (
            kitchen
            for kitchen in kitchen_list.kitchens
            if (language_code == "en" and kitchen.title_en == selected_kitchen_title)
            or (language_code == "ua" and kitchen.title_ua == selected_kitchen_title)
        ),
        None,
    )

    if not selected_kitchen:
        await message.answer(text_service.get_text("invalid_category", language_code))
        return

    content_type = "user-company"
    page = 1
    kitchen_id = str(selected_kitchen.id)

    await PaginationHandler.send_paginated_message(
        message,
        content_type,
        page,
        language_code,
        kitchen_id,
    )
