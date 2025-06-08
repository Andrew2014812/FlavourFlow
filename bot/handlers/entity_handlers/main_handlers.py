import json

from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from ...common.services.text_service import text_service
from ..main_keyboard_handlers import get_main_keyboard


async def show_main_menu(message: Message, language_code: str):
    keyboard = await get_main_keyboard(language_code, message.from_user.id)
    await message.answer(
        text_service.get_text("main_menu", language_code), reply_markup=keyboard
    )


async def render_warning_cart_message(
    callback, language_code, product_id, company_id, response
):
    await callback.message.answer(
        (
            f"Ви вже почали купувати у {response['detail']} компанії, видалити продукти з кошика?"
            if language_code == "ua"
            else f"You have already started buying in {response['detail']} company, do you want to remove the products from the cart?"
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Yes" if language_code == "en" else "Так",
                        callback_data=json.dumps(
                            {
                                "a": "clear_cart",
                                "e": str(product_id),
                                "c": str(company_id),
                            },
                            separators=(",", ":"),
                        ),
                    ),
                    InlineKeyboardButton(
                        text="No" if language_code == "en" else "Ні",
                        callback_data=json.dumps(
                            {
                                "a": "cancel_clear_cart",
                            },
                            separators=(",", ":"),
                        ),
                    ),
                ]
            ]
        ),
    )
