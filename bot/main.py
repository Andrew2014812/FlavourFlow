import asyncio
import logging
import time

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.common.database import create_db_and_tables
from bot.config import get_bot
from bot.handlers.callback_handlers import register_callback_handlers
from bot.handlers.command_handlers import register_command_handlers
from bot.handlers.entity_handlers.entity_handlers import (
    register_handlers as register_company_handlers,
)
from bot.handlers.entity_handlers.order_handlers import (
    register_handlers as register_order_handlers,
)
from bot.handlers.entity_handlers.product_handlers import (
    register_handlers as register_product_handlers,
)
from bot.handlers.entity_handlers.profile_handlers import register_profile_handlers
from bot.handlers.main_message_handlers import register_main_message_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    try:
        await create_db_and_tables()
        bot = await get_bot()
        dispatcher = Dispatcher(storage=MemoryStorage())

        register_command_handlers(dispatcher)
        register_callback_handlers(dispatcher)
        register_order_handlers(dispatcher)
        register_company_handlers(dispatcher)
        register_product_handlers(dispatcher)
        register_profile_handlers(dispatcher)
        register_main_message_handlers(dispatcher)

        logger.info("Starting bot polling...")
        await dispatcher.start_polling(bot)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


def run_bot_with_retries():
    max_retries = 10
    retry_count = 0
    backoff_time = 5

    while retry_count < max_retries:
        try:
            logger.info("Attempting to start bot...")
            asyncio.run(main())

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break

        except Exception as e:
            retry_count += 1
            logger.error(f"Bot crashed (attempt {retry_count}/{max_retries}): {e}")

            if retry_count >= max_retries:
                logger.critical("Max retries reached. Exiting.")
                break

            time.sleep(backoff_time)
            backoff_time *= 2


if __name__ == "__main__":
    run_bot_with_retries()
