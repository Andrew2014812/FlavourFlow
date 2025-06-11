import json

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..common.services import product_service
from ..common.services.cart_service import (
    add_to_cart,
    change_amount,
    clear_cart,
    remove_from_cart,
)
from ..common.services.company_service import company_service
from ..common.services.gastronomy_service import kitchen_service
from ..common.services.order_service import get_orders
from ..common.services.product_service import product_service
from ..common.services.text_service import text_service
from ..common.services.user_info_service import get_user_info
from ..common.services.wishlist_service import (
    add_to_wishlist,
    move_to_cart,
    remove_from_wishlist,
)
from ..handlers.entity_handlers.main_handlers import render_warning_cart_message
from ..handlers.entity_handlers.support_handlers import answer_message, ignore_message
from ..handlers.payment_handlers import proceed_payment
from .entity_handlers.entity_handlers import (
    handle_edit_company_image,
    handle_edit_company_kitchen,
    handle_edit_company_text,
    initiate_action,
    process_edit_company_kitchen,
    process_kitchen_selection,
    render_details,
)
from .entity_handlers.handler_utils import ActionType
from .entity_handlers.order_handlers import (
    handle_accept_order,
    handle_order_create,
    proceed_payment_on_delivery,
    send_admin_orders_info,
)
from .entity_handlers.product_handlers import (
    handle_edit_product_image,
    handle_edit_product_text,
)
from .entity_handlers.product_handlers import initiate_action as initiate_product_action
from .entity_handlers.product_handlers import render_details as render_product_details
from .pagination_handlers import update_paginated_message
from .reply_buttons_handlers import handle_admin, handle_restaurants

router = Router()

CONTENT_TYPES = {
    "COMPANY": "user-company",
    "ADMIN_COMPANY": "admin-company",
    "ADMIN_KITCHEN": "admin-kitchen",
    "ADMIN_PRODUCT": "admin-product",
    "PRODUCT": "product",
}

SERVICES = {
    "admin-company": company_service,
    "admin-kitchen": kitchen_service,
    "admin-product": product_service,
}


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    user_info = await get_user_info(callback.from_user.id)
    language_code = user_info.language_code
    if not language_code:
        language_code = "en"
    try:
        data = json.loads(callback.data)
        action = data.get("a")
        content_type = data.get("t")
        page = data.get("p", 1)
        item_id = data.get("id")
        extra_arg = data.get("e", "")
        kitchen_id = data.get("k", "")
        company_page = data.get("cp", page)

    except json.JSONDecodeError:
        data = callback.data.split(":")
        content_type = ""
        action = data[0]
        chat_id = data[1]
        user_id = data[2]
        message_id = data[3]

    if content_type == "admin-orders":
        orders = await get_orders(user_info)
        await send_admin_orders_info(user_info, orders)

    if action == "nav":
        await update_paginated_message(
            callback=callback,
            content_type=content_type,
            page=page,
            language_code=language_code,
            extra_arg=extra_arg,
            kitchen_id=kitchen_id,
        )

    elif action == "back":
        if content_type == CONTENT_TYPES["COMPANY"]:
            await callback.message.delete()
            await handle_restaurants(callback.message, language_code, state)

        elif content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await update_paginated_message(
                callback, "admin-company", page, language_code, extra_arg
            )
        elif content_type in [
            CONTENT_TYPES["ADMIN_COMPANY"],
            CONTENT_TYPES["ADMIN_KITCHEN"],
        ]:
            await handle_admin(
                callback.message, language_code, telegram_id=callback.from_user.id
            )

        elif content_type == "user-products":
            await update_paginated_message(
                callback=callback,
                content_type="user-company",
                page=company_page,
                language_code=language_code,
                extra_arg=extra_arg,
                kitchen_id=kitchen_id,
            )

        elif content_type.endswith("-details"):
            new_content_type = content_type.replace("-details", "")
            await update_paginated_message(
                callback, new_content_type, page, language_code, extra_arg
            )

    elif action == "add":
        entity_type = content_type.replace("admin-", "")
        if content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await initiate_product_action(
                callback, ActionType.ADD, page, language_code, state, int(extra_arg)
            )
        else:
            await initiate_action(
                callback, entity_type, ActionType.ADD, page, language_code, state
            )

    elif action == "edit":
        entity_type = content_type.replace("admin-", "")
        if content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await initiate_product_action(
                callback,
                ActionType.EDIT,
                page,
                language_code,
                state,
                int(extra_arg) if extra_arg else None,
                item_id,
            )
        else:
            await initiate_action(
                callback,
                entity_type,
                ActionType.EDIT,
                page,
                language_code,
                state,
                item_id,
            )

    elif action == "details":
        entity_type = content_type.replace("admin-", "")
        if content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await render_product_details(callback.message, item_id, page, language_code)
        else:
            await render_details(
                callback.message, entity_type, item_id, page, language_code
            )

    elif action == "delete":
        entity_type = content_type.replace("admin-", "")
        if content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await initiate_product_action(
                callback,
                ActionType.DELETE,
                page,
                language_code,
                state,
                int(extra_arg) if extra_arg else None,
                item_id,
            )
        else:
            await initiate_action(
                callback,
                entity_type,
                ActionType.DELETE,
                page,
                language_code,
                state,
                item_id,
            )

    elif action == "confirm_delete":
        service = SERVICES.get(content_type)
        if service:
            await service.delete(item_id, callback.from_user.id)
            await callback.message.edit_text(
                text_service.get_text("successful_deleting", language_code)
            )
            await update_paginated_message(
                callback, content_type, page, language_code, extra_arg
            )
            await state.clear()

    elif action == "cancel":
        await state.clear()
        await update_paginated_message(
            callback, content_type, page, language_code, extra_arg
        )

    elif action == "products":
        await update_paginated_message(
            callback, "admin-product", 1, language_code, extra_arg=str(item_id)
        )

    elif action == "list" and content_type == "user-products":
        await update_paginated_message(
            callback, "user-products", page, language_code, extra_arg
        )

    elif action == "add_to_cart" and content_type == "user-products":
        product_id = extra_arg
        company_id = data.get("c")
        response = await add_to_cart(callback.from_user.id, product_id, company_id)
        if response["status"] == 200:
            await callback.message.answer(
                "Product added to cart!"
                if language_code == "en"
                else "Продукт додано до кошика!"
            )
        elif response["status"] == 400:
            await render_warning_cart_message(
                callback, language_code, product_id, company_id, response
            )
        else:
            await callback.message.answer(
                "Something went wrong" if language_code == "en" else "Щось пішло не так"
            )

        await callback.answer()

    elif action == "clear_cart":
        product_id = extra_arg
        company_id = data.get("c")
        await clear_cart(callback.from_user.id)
        await callback.message.delete()
        await callback.message.answer(
            "Previous cart cleared!"
            if language_code == "en"
            else "Попередній кошик очищено!"
        )
        response = await add_to_cart(
            callback.from_user.id, int(product_id), int(company_id)
        )
        if response["status"] == 200:
            await callback.message.answer(
                "New product added to cart!"
                if language_code == "en"
                else "Новий продукт додано до кошика!"
            )
        callback.answer()

    elif action == "cancel_clear_cart":
        await callback.message.delete()
        callback.answer()

    elif action == "add_to_wishlist" and content_type == "user-products":
        product_id = extra_arg
        response = await add_to_wishlist(callback.from_user.id, product_id)
        if response["status"] == 200:
            await callback.message.answer(
                "Product added to wishlist!"
                if language_code == "en"
                else "Продукт додано до списку бажань!"
            )
        else:
            await callback.message.answer(
                "Something went wrong" if language_code == "en" else "Щось пішло не так"
            )

        await callback.answer()

    elif action == "plus":
        await change_amount(callback.from_user.id, item_id, 1)
        await update_paginated_message(
            callback,
            "cart",
            page,
            language_code,
            callback.from_user.id,
            with_back_button=False,
        )
        await callback.answer()

    elif action == "minus":
        await change_amount(callback.from_user.id, item_id, -1)
        await update_paginated_message(
            callback,
            "cart",
            page,
            language_code,
            callback.from_user.id,
            with_back_button=False,
        )
        await callback.answer()

    elif action == "remove" and content_type in ["cart", "wishlist"]:
        if content_type == "wishlist":
            await remove_from_wishlist(callback.from_user.id, item_id)
        else:
            await remove_from_cart(callback.from_user.id, item_id)

        await update_paginated_message(
            callback,
            content_type,
            1,
            language_code,
            callback.from_user.id,
            with_back_button=False,
        )
        await callback.answer()

    elif action == "m_cart" and content_type == "wl":
        product_id = extra_arg
        company_id = data.get("c")
        response = await move_to_cart(callback.from_user.id, item_id)
        if response["status"] == 200:
            await callback.message.answer(
                "Product moved to cart!"
                if language_code == "en"
                else "Продукт переміщено до кошика!"
            )
        elif response["status"] == 400:
            await render_warning_cart_message(
                callback, language_code, product_id, company_id, response
            )
            await callback.answer()
            return
        else:
            await callback.message.answer(
                "Something went wrong" if language_code == "en" else "Щось пішло не так"
            )
        await update_paginated_message(
            callback,
            "wishlist",
            1,
            language_code,
            callback.from_user.id,
            with_back_button=False,
        )
        await callback.answer()

    elif action == "order":
        await handle_order_create(callback.message, language_code, state)

    elif action == "accept":
        order_id = data.get("o")
        user_id = data.get("u")
        await handle_accept_order(
            callback.message,
            language_code,
            order_id=order_id,
            admin_id=callback.from_user.id,
            user_id=user_id,
        )

    elif action == "cancel_order":
        await callback.message.answer(
            "Order canceled!" if language_code == "en" else "Замовлення скасовано!"
        )
        await state.clear()
        await callback.answer()

    elif action == "pay":
        total_price = data.get("pr")
        order_id = data.get("o")
        await proceed_payment(
            callback.message, language_code, total_price=total_price, order_id=order_id
        )

    elif action == "pay_on_delivery":
        order_id = data.get("o")
        await proceed_payment_on_delivery(
            callback.message, order_id=order_id, user_id=callback.from_user.id
        )

    elif action == "edit_profile":
        await callback.message.answer(
            text_service.get_text("update_profile_instruction", language_code)
        )

    elif action == "s_answer":
        await answer_message(
            chat_id=chat_id,
            user_id=user_id,
            question_message_id=message_id,
            state=state,
            message_id=callback.message.message_id,
            language_code=language_code,
        )

    elif action == "s_ignore":
        await ignore_message(
            message_id=callback.message.message_id,
            chat_id=chat_id,
            user_id=user_id,
            question_message_id=message_id,
            language_code=language_code,
        )

    elif content_type == "select_kitchen_create":
        await process_kitchen_selection(callback, state, item_id)

    elif content_type == "select_kitchen_edit":
        await process_edit_company_kitchen(callback, state, item_id)

    elif content_type == "edit_company_text":
        await handle_edit_company_text(callback, state)

    elif content_type == "edit_company_kitchen":
        await handle_edit_company_kitchen(callback, state)

    elif content_type == "edit_company_image":
        await handle_edit_company_image(callback, state)

    elif content_type == "edit_product_text":
        await handle_edit_product_text(callback, state)

    elif content_type == "edit_product_image":
        await handle_edit_product_image(callback, state)

    await callback.answer()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
