import json

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..common.services import product_service
from ..common.services.cart_service import add_to_cart, change_amount
from ..common.services.company_service import company_service
from ..common.services.gastronomy_service import country_service, kitchen_service
from ..common.services.product_service import product_service
from ..common.services.text_service import text_service
from ..common.services.user_info_service import get_user_info
from .entity_handlers.entity_handlers import (
    handle_edit_company_country,
    handle_edit_company_image,
    handle_edit_company_kitchen,
    handle_edit_company_text,
    initiate_action,
    process_country_selection,
    process_edit_company_country,
    process_edit_company_kitchen,
    process_kitchen_selection,
    render_details,
)
from .entity_handlers.handler_utils import ActionType
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
    "ADMIN_COUNTRY": "admin-country",
    "ADMIN_KITCHEN": "admin-kitchen",
    "ADMIN_PRODUCT": "admin-product",
    "PRODUCT": "product",
}

SERVICES = {
    "admin-company": company_service,
    "admin-country": country_service,
    "admin-kitchen": kitchen_service,
    "admin-product": product_service,
}


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    user_info = await get_user_info(callback.from_user.id)
    language_code = user_info.language_code
    data = json.loads(callback.data)
    action = data.get("a")
    content_type = data.get("t")
    page = data.get("p", 1)
    item_id = data.get("id")
    extra_arg = data.get("e", "")
    kitchen_id = data.get("k", "")
    company_page = data.get("cp", page)

    if action == "nav":
        await update_paginated_message(
            callback, content_type, page, language_code, extra_arg
        )

    elif action == "back":
        if content_type == CONTENT_TYPES["COMPANY"]:
            await callback.message.delete()
            await handle_restaurants(callback.message, language_code)
        elif content_type == CONTENT_TYPES["ADMIN_PRODUCT"]:
            await update_paginated_message(
                callback, "admin-company", page, language_code, extra_arg
            )
        elif content_type in [
            CONTENT_TYPES["ADMIN_COMPANY"],
            CONTENT_TYPES["ADMIN_COUNTRY"],
            CONTENT_TYPES["ADMIN_KITCHEN"],
        ]:
            await handle_admin(
                callback.message, language_code, telegram_id=callback.from_user.id
            )
        elif content_type == "user-products":
            await update_paginated_message(
                callback,
                "user-company",
                company_page,
                language_code,
                extra_arg,
                kitchen_id,
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
                callback, content_type, page, language_code, extra_arg, make_send=True
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
        response = await add_to_cart(callback.from_user.id, product_id)
        if response["status"] == 200:
            await callback.message.answer(
                "Product added to cart!"
                if language_code == "en"
                else "Продукт додано до кошика!"
            )
        else:
            await callback.message.answer("something went wrong")

        await callback.answer()

    # elif action == "add_to_wishlist" and content_type == "user-products":
    #     product_id = extra_arg
    #     await callback.message.answer(
    #         "Product added to wishlist!"
    #         if language_code == "en"
    #         else "Продукт додано до списку бажань!"
    #     )
    #     await callback.answer()

    elif action == "plus_quantity":
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

    elif action == "minus_quantity":
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

    elif action == "edit_profile":
        await callback.message.answer(
            text_service.get_text("update_profile_instruction", language_code)
        )

    elif content_type == "select_country_create":
        await process_country_selection(callback, state, item_id)

    elif content_type == "select_kitchen_create":
        await process_kitchen_selection(callback, state, item_id)

    elif content_type == "select_country_edit":
        await process_edit_company_country(callback, state, item_id)

    elif content_type == "select_kitchen_edit":
        await process_edit_company_kitchen(callback, state, item_id)

    elif content_type == "edit_company_text":
        await handle_edit_company_text(callback, state)

    elif content_type == "edit_company_country":
        await handle_edit_company_country(callback, state)

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
