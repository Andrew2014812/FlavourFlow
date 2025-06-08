import json
from functools import wraps
from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.order.schemas import OrderResponse
from api.app.user.schemas import UserResponseMe

from ..common.services.order_service import get_paid_orders
from ..common.services.text_service import text_service
from ..common.services.user_info_service import get_user_info
from ..common.services.user_service import get_user
from ..config import get_bot
from ..handlers.entity_handlers.main_handlers import show_main_menu
from ..handlers.entity_handlers.order_handlers import render_orders
from ..handlers.entity_handlers.product_handlers import render_user_recommendations
from ..handlers.entity_handlers.support_handlers import Form
from ..handlers.main_keyboard_handlers import (
    get_admin_panel_keyboard,
    get_language_keyboard,
)
from ..handlers.pagination_handlers import send_paginated_message
from .main_keyboard_handlers import get_kitchens_keyboard

button_handlers = {}


def register_button_handler(*texts):
    def decorator(func):
        for text in texts:
            button_handlers[text] = func
        return func

    return decorator


def admin_required(func):
    @wraps(func)
    async def wrapper(message: Message, language_code: str, **kwargs):
        user = await get_user(message.from_user.id) or await get_user(
            kwargs.get("telegram_id", message.from_user.id)
        )

        if not user:
            await message.answer(
                text_service.get_text("select_language", "ua"),
                reply_markup=get_language_keyboard(),
            )
            return

        if user.role != "admin":
            await message.answer(text_service.get_text("no_access", language_code))
            return

        return await func(message, language_code, **kwargs)

    return wrapper


@register_button_handler(
    text_service.buttons["en"]["profile"], text_service.buttons["ua"]["profile"]
)
async def handle_profile(message: Message, language_code: str, _: FSMContext = None):
    user_data: UserResponseMe = await get_user(message.from_user.id)

    if not user_data:
        await message.answer(
            text_service.get_text("select_language", "ua"),
            reply_markup=get_language_keyboard(),
        )
        return

    last_name = user_data.last_name or ""
    profile_data = {
        "name": f"{user_data.first_name} {last_name}",
        "language": "Українська" if language_code == "ua" else "English",
        "phone": user_data.phone_number,
    }

    profile_text = text_service.get_text("profile_message", language_code).format(
        **profile_data
    )

    callback_data = json.dumps({"a": "edit_profile"}, separators=(",", ":"))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text_service.get_text("profile_edit", language_code),
                    callback_data=callback_data,
                ),
            ]
        ]
    )

    await message.answer(profile_text, reply_markup=keyboard)


@register_button_handler(
    text_service.buttons["en"]["restaurants"], text_service.buttons["ua"]["restaurants"]
)
async def handle_restaurants(
    message: Message, language_code: str, _: FSMContext = None
):
    await message.answer(
        text_service.get_text("select_category", language_code),
        reply_markup=await get_kitchens_keyboard(language_code),
    )


@register_button_handler(
    text_service.buttons["en"]["back"], text_service.buttons["ua"]["back"]
)
async def handle_back(message: Message, language_code: str, _: FSMContext = None):
    await show_main_menu(message, language_code)


@register_button_handler(
    text_service.buttons["en"]["cart"], text_service.buttons["ua"]["cart"]
)
async def handle_cart(message: Message, language_code: str, _: FSMContext = None):
    await send_paginated_message(
        message, "cart", 1, language_code, message.from_user.id, with_back_button=False
    )


@register_button_handler(
    text_service.buttons["en"]["wishlist"], text_service.buttons["ua"]["wishlist"]
)
async def handle_wishlist(message: Message, language_code: str, _: FSMContext = None):
    await send_paginated_message(
        message,
        "wishlist",
        1,
        language_code,
        message.from_user.id,
        with_back_button=False,
    )


@register_button_handler(
    text_service.buttons["en"]["admin_panel"], text_service.buttons["ua"]["admin_panel"]
)
@admin_required
async def handle_admin(
    message: Message, language_code: str, _: FSMContext = None, **kwargs
):
    text = text_service.get_text("select_admin_action", language_code)
    keyboard = get_admin_panel_keyboard(language_code)

    if kwargs.get("telegram_id"):
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@register_button_handler(
    text_service.buttons["en"]["orders"],
    text_service.buttons["ua"]["orders"],
)
async def handle_orders(message: Message, language_code: str, _: FSMContext = None):
    orders: List[OrderResponse] = await get_paid_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "You have no orders" if language_code == "en" else "У вас немає замовлень"
        )
        return
    await message.answer(
        "Your orders:" if language_code == "en" else "Ваші замовлення:"
    )

    bot = await get_bot()
    await render_orders(bot, orders, language_code, message.from_user.id)
    await bot.session.close()


@register_button_handler(
    text_service.buttons["en"]["recommendations"],
    text_service.buttons["ua"]["recommendations"],
)
async def handle_recommendations(message: Message, _: str, state: FSMContext = None):
    await render_user_recommendations(message, message.from_user.id)


@register_button_handler(
    text_service.buttons["en"]["support"], text_service.buttons["ua"]["support"]
)
async def handle_help(message: Message, language_code: str, state: FSMContext = None):
    user_info = await get_user_info(message.from_user.id)
    if not user_info.is_support_pending:
        await message.answer(
            "Enter your question" if language_code == "en" else "Введіть ваше питання"
        )
        await state.update_data(language_code=language_code)
        await state.set_state(Form.support_question)
    else:
        await message.answer(
            "You have already sent a message, please wait an answer"
            if language_code == "en"
            else "Ви вже надіслали повідомлення, будь ласка, очіквайте відповідь"
        )
