import json

from aiogram import Router
from aiogram.types import LabeledPrice, Message

from bot.config import get_bot

from ..config import PAYMENTS_TOKEN, get_bot

router = Router()


async def proceed_payment(
    message: Message,
    language_code: str,
    order_id: int,
    total_price: float,
    **_,
):
    bot = await get_bot()

    payload = json.dumps({"order_id": order_id})

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Оплата замовлення",
        description=(
            "Оплата замовлення через Redsys"
            if language_code == "ua"
            else "Order payment via Redsys"
        ),
        provider_token=PAYMENTS_TOKEN,
        currency="USD",
        prices=[
            LabeledPrice(
                label="Товар" if language_code == "ua" else "Product",
                amount=total_price * 100,
            )
        ],
        payload=payload,
        start_parameter="buy-product",
        photo_url="https://example.com/product.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
    )

    await bot.session.close()
