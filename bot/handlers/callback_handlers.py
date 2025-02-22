from aiogram import types, Router, Dispatcher
from aiogram.types import CallbackQuery

from bot.common.bot_crud import get_user_info

router = Router()
callback_handlers = {}


def register_callback_handler(callback_prefix: str):
    def decorator(func):
        callback_handlers[callback_prefix] = func
        return func

    return decorator


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    language_code = get_user_info(telegram_id).language_code

    for prefix, handler in callback_handlers.items():
        if callback.data.startswith(prefix):
            await handler(callback, language_code)
            return

    await callback.answer("Unknown action")


@register_callback_handler("edit_profile")
async def start_edit_profile(callback: types.CallbackQuery, language_code: str):
    instruction = (
        "Enter the fields you want to update in one message. Use this format:\n"
        "Name: [new name]\n"
        "Phone: [new phone number]\n"
        "Bonuses: [new bonuses]\n\n"
        "Example (update only what you need):\n"
        "Phone: +380991234567\n"
        "Bonuses: 200"
        if language_code == "en" else
        "Введіть поля, які хочете оновити, в одному повідомленні. Використовуйте цей формат:\n"
        "Ім'я: [нове ім'я]\n"
        "Телефон: [новий номер телефону]\n"
        "Бонуси: [нові бонуси]\n\n"
        "Приклад (оновіть лише потрібне):\n"
        "Телефон: +380991234567\n"
        "Бонуси: 200"
    )
    await callback.message.answer(instruction)
    await callback.answer()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
