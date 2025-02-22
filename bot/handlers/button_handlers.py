from aiogram.types import Message

from bot.config import buttons
from bot.handlers.command_handlers import get_text

button_handlers = {}


def register_button_handler(*button_texts):
    def decorator(func):
        for text in button_texts:
            button_handlers[text] = func
        return func

    return decorator


@register_button_handler("Настройк")
async def handle_settings(message: Message, language: str):
    await message.answer(get_text("settings_message", language))


@register_button_handler(buttons["en"]["profile"], buttons["ua"]["profile"])
async def handle_profile(message: Message, language: str):
    await message.answer(get_text("profile_message", language))


@register_button_handler("Помощь")
async def handle_help(message: Message, language: str):
    await message.answer(get_text("help_message", language))
