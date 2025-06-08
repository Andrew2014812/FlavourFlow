import json

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from api.app.order.schemas import OrderCreate, OrderItemCreate

from ...common.services.cart_service import get_cart_items
from ...common.services.order_service import create_order
from ...common.services.text_service import text_service
from ...handlers.entity_handlers.handler_utils import convert_raw_text_to_valid_dict

router = Router()


class Form(StatesGroup):
    process_order_details = State()


FIELD_MAPPING = {
    "Address:": "address",
    "time:": "time",
    "Адреса:": "address",
    "Час:": "time",
}


async def handle_order_create(
    message: Message, language_code: str, state: FSMContext
) -> None:

    await message.answer(text_service.get_text("order_instruction", language_code))
    await message.answer(
        text_service.get_text("order_example_with_time", language_code)
    )
    await message.answer(
        text_service.get_text("order_example_without_time", language_code)
    )
    await state.update_data(language_code=language_code)
    await state.set_state(Form.process_order_details)


@router.message(Form.process_order_details)
async def handle_order_details(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    language_code = state_data.get("language_code")
    cart_items = await get_cart_items(message.from_user.id, return_all=True)
    result = await convert_raw_text_to_valid_dict(
        message.text, FIELD_MAPPING, is_allow_empty=True
    )

    caption = ""
    order_items = []
    total_price = 0
    for item in cart_items:
        total_price += item.price * item.quantity
        order_items.append(OrderItemCreate(**item.model_dump()))
        caption += f"{item.product_title_ua} - {item.quantity} - ${item.price * item.quantity}.\n"

    address_name = "Address" if language_code == "en" else "Адреса"
    time_name = "Time" if language_code == "en" else "Час"
    caption += f"\n{address_name}: {result['address']}\n{time_name}: {result.get('time', "Не вказано" if language_code == "ua" else "Not specified")}\n\n"
    await message.answer("Ваше замовлення:" if language_code == "ua" else "Your order:")

    order_create = OrderCreate(
        total_price=total_price,
        order_items=order_items,
        address=result["address"],
        time=result.get("time", None),
    )
    order = await create_order(order_create=order_create, user_id=message.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Pay" if language_code == "en" else "Оплатити",
            callback_data=json.dumps(
                {
                    "a": "pay",
                    "pr": total_price,
                    "o": order.id,
                },
                separators=(",", ":"),
            ),
        )
    )
    await message.answer(caption, reply_markup=builder.as_markup())
    await state.clear()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
