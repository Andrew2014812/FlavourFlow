from aiogram import Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from ..common.services.text_service import text_service
from ..handlers.entity_handlers.product_handlers import render_user_recommendations
from ..handlers.main_keyboard_handlers import get_language_keyboard

router = Router()


@router.message(Command(commands=["start", "language"]))
async def cmd_start(message: Message):
    await message.answer(
        text_service.get_text("select_language", "ua"),
        reply_markup=get_language_keyboard(),
    )


@router.message(Command(commands=["recommendations"]))
async def cmd_recommendations(message: Message):
    await render_user_recommendations(message)


def register_command_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
