from aiogram import Router
from aiogram.types import LabeledPrice, Message

from bot.config import get_bot

from ..config import PAYMENTS_TOKEN, get_bot

router = Router()


async def proceed_payment(message: Message, language_code: str, **_):
    bot = await get_bot()

    if PAYMENTS_TOKEN.split(":")[1] == "TEST":
        await bot.send_message(message.chat.id, "Это тестовый платеж!")

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка товара",
        description="Оплата за товар через Redsys",
        provider_token=PAYMENTS_TOKEN,
        currency="USD",
        prices=[LabeledPrice(label="Товар", amount=1000)],
        payload="unique-invoice-payload-123",
        start_parameter="buy-product",
        photo_url="https://example.com/product.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
    )

    await bot.session.close()
