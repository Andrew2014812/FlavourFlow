import json
from functools import wraps
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.order.schemas import OrderResponse
from api.app.user.schemas import UserResponseMe
from bot.common.services.order_service import get_paid_orders

from ..common.services.text_service import text_service
from ..common.services.user_service import get_user
from ..handlers.entity_handlers.main_handlers import show_main_menu
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
async def handle_profile(message: Message, language_code: str):
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
async def handle_restaurants(message: Message, language_code: str):
    await message.answer(
        text_service.get_text("select_category", language_code),
        reply_markup=await get_kitchens_keyboard(language_code),
    )


@register_button_handler(
    text_service.buttons["en"]["back"], text_service.buttons["ua"]["back"]
)
async def handle_back(message: Message, language_code: str):
    await show_main_menu(message, language_code)


@register_button_handler(
    text_service.buttons["en"]["cart"], text_service.buttons["ua"]["cart"]
)
async def handle_cart(message: Message, language_code: str):
    await send_paginated_message(
        message, "cart", 1, language_code, message.from_user.id, with_back_button=False
    )


@register_button_handler(
    text_service.buttons["en"]["admin_panel"], text_service.buttons["ua"]["admin_panel"]
)
@admin_required
async def handle_admin(message: Message, language_code: str, **kwargs):
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
async def handle_orders(message: Message, language_code: str):
    orders: List[OrderResponse] = await get_paid_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "You have no orders" if language_code == "en" else "У вас немає замовлень"
        )
        return
    await message.answer(
        "Your orders:" if language_code == "en" else "Ваші замовлення:"
    )

    for order in orders:
        order_address_name = "Address" if language_code == "en" else "Адреса"
        order_time_name = "Time" if language_code == "en" else "Час"
        order_total_price_name = "Total price" if language_code == "en" else "Всього"

        order_message = ""

        for order_item in order.order_items:
            order_item_caption = "Item" if language_code == "en" else "Позиція"
            order_item_price_name = "Price" if language_code == "en" else "Ціна"
            order_item_quantity_name = (
                "Quantity" if language_code == "en" else "Кількість"
            )

            order_message += f"{order_item_caption}: {order_item.product.title_ua if language_code == 'ua' else order_item.product.title_en} \n"
            order_message += f"{order_item_quantity_name}: {order_item.quantity}\n"
            order_message += f"{order_item_price_name}: ${order_item.product.price}\n\n"

        order_message += f"{order_address_name}: {order.address}\n"
        order_message += f"{order_time_name}: {order.time}\n"
        order_message += f"{order_total_price_name}: ${order.total_price}"

        await message.answer(order_message)
