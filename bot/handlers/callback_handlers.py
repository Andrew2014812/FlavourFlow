import json

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..common.services.company_service import company_service
from ..common.services.gastronomy_service import country_service, kitchen_service
from ..common.services.text_service import text_service
from ..common.services.user_info_service import get_user_info
from .entity_handlers.entity_handlers import initiate_action, render_details
from .entity_handlers.handler_utils import ActionType
from .pagination_handlers import update_paginated_message
from .reply_buttons_handlers import handle_admin, handle_restaurants

router = Router()

CONTENT_TYPES = {
    "COMPANY": "user-company",
    "ADMIN_COMPANY": "admin-company",
    "ADMIN_COUNTRY": "admin-country",
    "ADMIN_KITCHEN": "admin-kitchen",
    "PRODUCT": "product",
}

SERVICES = {
    "admin-company": company_service,
    "admin-country": country_service,
    "admin-kitchen": kitchen_service,
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

    if action == "nav":
        await update_paginated_message(
            callback, content_type, page, language_code, extra_arg
        )

    elif action == "back":
        if content_type == CONTENT_TYPES["COMPANY"]:
            await callback.message.delete()
            await handle_restaurants(callback.message, language_code)
        elif content_type in [
            CONTENT_TYPES["ADMIN_COMPANY"],
            CONTENT_TYPES["ADMIN_COUNTRY"],
            CONTENT_TYPES["ADMIN_KITCHEN"],
        ]:
            await handle_admin(
                callback.message, language_code, telegram_id=callback.from_user.id
            )
        elif content_type.endswith("-details"):
            new_content_type = content_type.replace("-details", "")
            await update_paginated_message(
                callback, new_content_type, page, language_code
            )

    elif action == "add":
        entity_type = content_type.replace("admin-", "")
        await initiate_action(
            callback, entity_type, ActionType.ADD, page, language_code, state
        )

    elif action == "edit":
        entity_type = content_type.replace("admin-", "")
        await initiate_action(
            callback, entity_type, ActionType.EDIT, page, language_code, state, item_id
        )

    elif action == "details":
        entity_type = content_type.replace("admin-", "")
        await render_details(
            callback.message, entity_type, item_id, page, language_code
        )

    elif action == "delete":
        entity_type = content_type.replace("admin-", "")
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
                callback, content_type, page, language_code, make_send=True
            )
            await state.clear()

    elif action == "cancel":
        await state.clear()
        await update_paginated_message(callback, content_type, page, language_code)

    elif action == "edit_profile":
        await callback.message.answer(
            text_service.get_text("update_profile_instruction", language_code)
        )

    await callback.answer()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
