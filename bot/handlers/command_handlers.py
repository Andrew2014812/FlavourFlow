from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from bot.common.utils import get_text
from bot.handlers.display_handlers import get_language_keyboard

router = Router()


@router.message(Command(commands=["start", "language"]))
async def cmd_start(message: Message):
    await message.answer(
        get_text("select_language", "ua"),
        reply_markup=get_language_keyboard()
    )

def register_command_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
