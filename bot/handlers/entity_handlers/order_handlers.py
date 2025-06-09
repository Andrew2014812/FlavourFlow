import json
from typing import List

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from api.app.order.schemas import OrderCreate, OrderItemCreate, OrderResponse
from api.app.user.schemas import UserResponse

from ...common.models import UserInfo
from ...common.services.cart_service import get_cart_items
from ...common.services.order_service import (
    accept_order,
    create_order,
    get_order_by_id,
    update_order_purchase_info,
)
from ...common.services.text_service import text_service
from ...common.services.user_info_service import get_user_info
from ...common.services.user_service import retrieve_admins
from ...config import get_bot
from ...handlers.entity_handlers.handler_utils import convert_raw_text_to_valid_dict

router = Router()


class Form(StatesGroup):
    process_order_details = State()
    proceed_payment = State()


FIELD_MAPPING = {
    "Address:": "address",
    "time:": "time",
    "Адреса:": "address",
    "Час:": "time",
}


async def handle_order_create(
    message: Message, language_code: str, state: FSMContext
) -> None:

    await message.answer(
        text_service.get_text("order_instruction", language_code),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=("Cancel" if language_code == "en" else "Відмінити"),
                        callback_data=json.dumps(
                            {
                                "a": "cancel_order",
                            },
                            separators=(",", ":"),
                        ),
                    )
                ]
            ]
        ),
    )
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

    await proceed_payment(
        message, state, language_code, order.id, order.total_price, caption
    )


async def proceed_payment(
    message: Message,
    state: FSMContext,
    language_code: str,
    order_id: int,
    total_price: int,
    caption: str,
):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Pay" if language_code == "en" else "Оплатити",
            callback_data=json.dumps(
                {
                    "a": "pay",
                    "pr": total_price,
                    "o": order_id,
                },
                separators=(",", ":"),
            ),
        ),
        InlineKeyboardButton(
            text="Оплата при отриманні" if language_code == "ua" else "Pay on delivery",
            callback_data=json.dumps(
                {"a": "pay_on_delivery", "o": order_id}, separators=(",", ":")
            ),
        ),
    )
    await message.answer(caption, reply_markup=builder.as_markup())
    await state.clear()


async def proceed_payment_on_delivery(
    message: Message,
    order_id: int,
    user_id: int,
):
    await confirm_order(message, order_id, await get_user_info(user_id))


async def confirm_order(message: Message, order_id: int, user_info: UserInfo):
    await update_order_purchase_info(order_id=order_id, user_id=user_info.telegram_id)
    await message.answer(
        f"Замовлення №{order_id} в обробці ви отримаєте повідомлення при прийнятті!"
        if user_info.language_code == "ua"
        else f"Your order #{order_id} will be processed and you will receive a notification when it is accepted!"
    )
    await send_order_info_to_admins(user_info.telegram_id, order_id)


async def render_orders(
    bot: Bot, orders: List[OrderResponse], language_code: str, user_id: int
):
    for order in orders:
        order_status_en = "Accepted" if order.is_submitted else "Pending"
        order_status_ua = "Прийнято" if order.is_submitted else "В обробці"
        order_status_name = "Status" if language_code == "en" else "Статус"
        order_address_name = "Address" if language_code == "en" else "Адреса"
        order_time_name = "Time" if language_code == "en" else "Час"
        order_total_price_name = "Total price" if language_code == "en" else "Всього"

        order_message = f"№{order.id}\n{order_status_name}: {order_status_en if language_code == 'en' else order_status_ua}\n\n"

        for order_item in order.order_items:
            order_item_caption = "Item" if language_code == "en" else "Позиція"
            order_item_price_name = "Price" if language_code == "en" else "Ціна"
            order_item_quantity_name = (
                "Quantity" if language_code == "en" else "Кількість"
            )

            order_message += f"{order_item_caption}: {order_item.product.title_ua if language_code == 'ua' else order_item.product.title_en} \n"
            order_message += f"{order_item_quantity_name}: {order_item.quantity}\n"
            order_message += f"{order_item_price_name}: ${order_item.product.price}\n\n"

        order_message += f"{order_address_name}: {order.address}\n"
        order_message += f"{order_time_name}: {order.time}\n"
        order_message += f"{order_total_price_name}: ${order.total_price}"

        await bot.send_message(user_id, order_message)


async def send_order_info_to_admins(user_id: int, order_id: int):
    bot = await get_bot()
    admins = await retrieve_admins()
    order = await get_order_by_id(order_id=order_id, user_id=user_id)

    for admin in admins:
        user_info = await get_user_info(admin.telegram_id)
        await bot.send_message(
            admin.telegram_id,
            (
                "New order received!"
                if user_info.language_code == "en"
                else "Нове замовлення отримано!"
            ),
        )
        await send_admin_orders_info(bot, user_info, admin, [order])

    await bot.session.close()


async def send_admin_orders_info(
    bot: Bot,
    user_info: UserInfo,
    admin: UserResponse,
    orders: List[OrderResponse],
):

    for order in orders:
        if user_info.language_code == "en":
            caption = f"Order #{order.id}\n\n Client information:\nName: {order.user.first_name} {order.user.last_name}\nPhone: {order.user.phone_number}\n\nDetails:"
        else:
            caption = f"Замовлення #{order.id}\n\nПерсональні дані клієнта:\nІм'я: {order.user.first_name} {order.user.last_name if order.user.last_name else ''}\nТелефон: {order.user.phone_number}\n\nДеталі:"

        await bot.send_message(
            chat_id=admin.telegram_id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "Accept"
                                if user_info.language_code == "en"
                                else "Прийняти"
                            ),
                            callback_data=json.dumps(
                                {
                                    "a": "accept",
                                    "o": order.id,
                                    "u": order.user.telegram_id,
                                },
                                separators=(",", ":"),
                            ),
                        )
                    ]
                ]
            ),
        )
        await render_orders(
            bot=bot,
            orders=[order],
            language_code=user_info.language_code,
            user_id=admin.telegram_id,
        ),


async def handle_accept_order(
    message: Message,
    language_code: str,
    order_id: int,
    admin_id: int,
    user_id: int,
):
    response = await accept_order(order_id=order_id, user_id=admin_id)
    if response["status"] == 400:
        await message.answer(
            "Order already accepted!"
            if language_code == "en"
            else "Замовлення вже прийнято!"
        )
        return

    await message.answer(
        "Order accepted successfully!"
        if language_code == "en"
        else "Замовлення успішно прийнято!"
    )
    bot = await get_bot()
    user_info = await get_user_info(user_id)
    await bot.send_message(
        user_id,
        (
            f"Your order №{order_id} has been accepted!"
            if user_info.language_code == "en"
            else f"Ваше замовлення №{order_id} прийнято!"
        ),
    )
    await bot.session.close()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
