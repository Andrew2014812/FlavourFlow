from typing import Callable, Union
from aiogram import types, Router, Dispatcher
from aiogram.types import CallbackQuery

from bot.common.services.text_service import text_service
from bot.common.services.user_info_service import get_user_info

router = Router()
callback_handlers = {}


def register_callback_handler(filter_arg: Union[str, Callable]):
    def decorator(func):
        if isinstance(filter_arg, str):
            filter_func = lambda data: data.startswith(filter_arg)
        else:
            filter_func = filter_arg

        callback_handlers[func] = filter_func
        return func

    return decorator


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    user_info = await get_user_info(telegram_id)
    language_code = user_info.language_code

    for handler, filter_func in callback_handlers.items():
        if filter_func(callback.data):
            await handler(callback, language_code)
            return

    await callback.answer("Unknown action")


@register_callback_handler("edit_profile")
async def start_edit_profile(callback: types.CallbackQuery, language_code: str):
    await callback.message.answer(
        text_service.get_text("update_profile_instruction", language_code)
    )
    await callback.answer()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
