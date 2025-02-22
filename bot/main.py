import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.common.database import create_db_and_tables
from bot.config import TG_TOKEN
from bot.handlers.callback_handlers import register_callback_handlers
from bot.handlers.command_handlers import register_command_handlers
from bot.handlers.message_handlers import register_message_handlers


async def main():
    create_db_and_tables()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TG_TOKEN)
    dispatcher = Dispatcher(storage=MemoryStorage())

    register_command_handlers(dispatcher)
    register_message_handlers(dispatcher)
    register_callback_handlers(dispatcher)

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
