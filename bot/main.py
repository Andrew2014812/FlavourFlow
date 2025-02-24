import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.common.database import create_db_and_tables
from bot.config import TG_TOKEN
from bot.handlers.command_handlers import register_command_handlers
from bot.handlers.callback_handlers import register_callback_handlers
from bot.handlers.main_message_handlers import register_main_message_handlers
from bot.handlers.profile.handlers import register_profile_handlers
from bot.handlers.company.handlers import register_company_handlers


async def main():
    create_db_and_tables()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TG_TOKEN)
    dispatcher = Dispatcher(storage=MemoryStorage())

    # register_company_handlers(dispatcher)
    register_profile_handlers(dispatcher)
    register_command_handlers(dispatcher)
    register_callback_handlers(dispatcher)
    register_main_message_handlers(dispatcher)

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
