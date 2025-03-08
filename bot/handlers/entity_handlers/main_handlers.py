from aiogram.types import Message

from bot.common.services.text_service import text_service
from bot.handlers.main_keyboard_handlers import get_main_keyboard


async def show_main_menu(message: Message, language_code: str):
    keyboard = await get_main_keyboard(language_code, message.from_user.id)
    await message.answer(
        text_service.get_text("main_menu", language_code), reply_markup=keyboard
    )
