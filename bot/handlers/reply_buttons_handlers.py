import json
from functools import wraps

import stripe
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from api.app.user.schemas import UserResponseMe

from ..common.services.text_service import text_service
from ..common.services.user_service import get_user
from ..handlers.entity_handlers.main_handlers import show_main_menu
from ..handlers.main_keyboard_handlers import (
    get_admin_panel_keyboard,
    get_language_keyboard,
)
from ..handlers.pagination_handlers import get_category_keyboard, send_paginated_message

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
        "bonuses": user_data.bonuses,
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
        reply_markup=await get_category_keyboard(language_code),
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


stripe.api_key = ""


@register_button_handler(
    text_service.buttons["en"]["test_payment"],
    text_service.buttons["ua"]["test_payment"],
)
async def handle_payment(message: Message, language_code: str, **kwargs):
    # Создание сессии Stripe Checkout
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Тестовый товар",
                        },
                        "unit_amount": 1000,  # 10.00 USD (в центах)
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        # Отправка ссылки на оплату
        payment_url = session.url
        payment_message = (
            "Для тестирования оплаты переходите по ссылке: " + f": {payment_url}"
        )
        await message.answer(payment_message)
    except Exception as e:
        error_message = "error in handle_payment: " + str(e)
        await message.answer(error_message)
