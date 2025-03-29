import json
from typing import Callable, Dict, Optional, Union

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..common.services.gastronomy_service import country_service, kitchen_service
from ..common.services.text_service import text_service
from ..common.services.user_info_service import get_user_info
from .entity_handlers.gastronomy_handlers import (
    ActionType,
    GenericGastronomyHandler,
    country_handler,
    kitchen_handler,
)
from .pagination_handlers import company_admin_handler, company_handler
from .pagination_handlers import country_handler as country_pagination_handler
from .pagination_handlers import create_pagination_handler
from .pagination_handlers import kitchen_handler as kitchen_pagination_handler
from .pagination_handlers import product_handler
from .reply_buttons_handlers import handle_admin, handle_restaurants

router = Router()

CONTENT_TYPES = {
    "COMPANY": "user-company",
    "ADMIN_COMPANY": "admin-company",
    "ADMIN_COUNTRY": "admin-country",
    "ADMIN_KITCHEN": "admin-kitchen",
    "PRODUCT": "product",
}


class Action:
    NAV = "nav"
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"
    DETAILS = "details"
    BACK = "back"
    CANCEL = "cancel"
    CONFIRM_DELETE = "confirm_delete"


class HandlerRegistry:
    def __init__(self):
        self.handlers: Dict[Callable, Callable] = {}

    def register(self, filter_arg: Union[str, Callable]):
        def decorator(func):
            if isinstance(filter_arg, str):
                filter_func = lambda data: data.startswith(filter_arg)

            else:
                filter_func = filter_arg

            self.handlers[func] = filter_func
            return func

        return decorator

    async def process(self, callback: CallbackQuery, **kwargs):
        for handler, filter_func in self.handlers.items():
            try:
                if filter_func(callback.data):
                    await handler(callback, **kwargs)
                    return True
            except (json.JSONDecodeError, KeyError):
                continue
        return False


registry = HandlerRegistry()


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    user_info = await get_user_info(telegram_id)
    language_code = user_info.language_code

    if not await registry.process(callback, language_code=language_code, state=state):
        await callback.answer("Unknown action")


async def create_admin_handler(handler: GenericGastronomyHandler):
    return create_pagination_handler(
        f"admin-{handler.entity_type}", handler.render_list_content
    )


async def handle_gastronomy_action(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    handler: GenericGastronomyHandler,
    action: ActionType,
    page: int,
    item_id: Optional[int] = None,
):
    admin_handler = await create_admin_handler(handler)

    await handler.initiate_action(
        callback, language_code, state, action, page, admin_handler, item_id
    )


async def handle_navigation(
    callback: CallbackQuery,
    language_code: str,
    content_type: str,
    page: int = 1,
    **kwargs,
):
    handlers = {
        CONTENT_TYPES["ADMIN_COMPANY"]: company_admin_handler,
        CONTENT_TYPES["ADMIN_COUNTRY"]: country_pagination_handler,
        CONTENT_TYPES["ADMIN_KITCHEN"]: kitchen_pagination_handler,
        CONTENT_TYPES["COMPANY"]: company_handler,
        CONTENT_TYPES["PRODUCT"]: product_handler,
    }

    if handler := handlers.get(content_type):
        await handler(callback, language_code, page=page, **kwargs)


def create_callback_data(
    action: str, content_type: str, page: int = 1, **kwargs
) -> str:
    data = {"a": action, "p": page, "t": content_type, **kwargs}
    return json.dumps(data, separators=(",", ":"))


async def modify_callback(
    callback: CallbackQuery, action: str, content_type: str, page: int = 1, **kwargs
) -> CallbackQuery:
    new_data = create_callback_data(action, content_type, page, **kwargs)

    return callback.model_copy(update={"data": new_data})


async def handle_back_action(
    callback: CallbackQuery, language_code: str, content_type: str, page: int = 1
):
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

    elif content_type == "admin-country-details":
        await handle_navigation(
            callback, language_code, CONTENT_TYPES["ADMIN_COUNTRY"], page
        )

    elif content_type == "admin-kitchen-details":
        await handle_navigation(
            callback, language_code, CONTENT_TYPES["ADMIN_KITCHEN"], page
        )


@registry.register(lambda data: json.loads(data).get("t") == "category")
async def handle_category_selection(
    callback: CallbackQuery, language_code: str, **kwargs
):
    data = json.loads(callback.data)
    category = data["v"].capitalize()
    new_callback = await modify_callback(
        callback, Action.NAV, CONTENT_TYPES["COMPANY"], 1, e=category
    )
    await handle_navigation(new_callback, language_code, CONTENT_TYPES["COMPANY"])


@registry.register(lambda data: json.loads(data).get("a") == Action.BACK)
async def handle_back_navigation(callback: CallbackQuery, language_code: str, **kwargs):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data.get("p", 1)

    if content_type == "admin-country-details":
        new_callback = await modify_callback(
            callback, Action.NAV, CONTENT_TYPES["ADMIN_COUNTRY"], page
        )
        await handle_navigation(
            new_callback, language_code, CONTENT_TYPES["ADMIN_COUNTRY"], page
        )

    elif content_type == "admin-kitchen-details":
        new_callback = await modify_callback(
            callback, Action.NAV, CONTENT_TYPES["ADMIN_KITCHEN"], page
        )
        await handle_navigation(
            new_callback, language_code, CONTENT_TYPES["ADMIN_KITCHEN"], page
        )

    else:
        await handle_back_action(callback, language_code, content_type, page)

    await callback.answer()


@registry.register(lambda data: json.loads(data).get("a") == Action.CANCEL)
async def handle_cancel_action(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]
    await state.clear()

    if content_type in [CONTENT_TYPES["ADMIN_COUNTRY"], CONTENT_TYPES["ADMIN_KITCHEN"]]:
        new_callback = await modify_callback(callback, Action.NAV, content_type, page)
        await handle_navigation(new_callback, language_code, content_type)

    await callback.answer()


@registry.register(lambda data: json.loads(data).get("a") == Action.ADD)
async def handle_add_action(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]

    handlers = {
        CONTENT_TYPES["ADMIN_COUNTRY"]: (country_handler, ActionType.ADD),
        CONTENT_TYPES["ADMIN_KITCHEN"]: (kitchen_handler, ActionType.ADD),
    }

    if handler_info := handlers.get(content_type):
        handler, action = handler_info
        await handle_gastronomy_action(
            callback,
            language_code,
            state,
            handler,
            action,
            page,
        )


@registry.register(lambda data: json.loads(data).get("a") == Action.EDIT)
async def handle_edit_action(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]
    item_id = data["id"]

    handlers = {
        CONTENT_TYPES["ADMIN_COUNTRY"]: (country_handler, ActionType.EDIT),
        CONTENT_TYPES["ADMIN_KITCHEN"]: (kitchen_handler, ActionType.EDIT),
    }

    if handler_info := handlers.get(content_type):
        handler, action = handler_info
        await handle_gastronomy_action(
            callback,
            language_code,
            state,
            handler,
            action,
            page,
            item_id,
        )


@registry.register(lambda data: json.loads(data).get("a") == Action.DETAILS)
async def handle_item_details(callback: CallbackQuery, language_code: str, **kwargs):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]
    item_id = data["id"]

    handlers = {
        CONTENT_TYPES["ADMIN_COUNTRY"]: country_handler,
        CONTENT_TYPES["ADMIN_KITCHEN"]: kitchen_handler,
    }

    if handler := handlers.get(content_type):
        await handler.render_details_content(
            callback.message,
            page,
            language_code,
            item_id,
        )

    await callback.answer()


@registry.register(lambda data: json.loads(data).get("a") == Action.DELETE)
async def handle_delete_action(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]
    item_id = data["id"]

    handlers = {
        CONTENT_TYPES["ADMIN_COUNTRY"]: (country_handler, ActionType.DELETE),
        CONTENT_TYPES["ADMIN_KITCHEN"]: (kitchen_handler, ActionType.DELETE),
    }

    if handler_info := handlers.get(content_type):
        handler, action = handler_info
        await handle_gastronomy_action(
            callback,
            language_code,
            state,
            handler,
            action,
            page,
            item_id,
        )

    await callback.answer()


@registry.register(lambda data: json.loads(data).get("a") == Action.CONFIRM_DELETE)
async def handle_confirm_delete(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    data = json.loads(callback.data)
    content_type = data["t"]
    page = data["p"]
    item_id = data["id"]

    services = {
        CONTENT_TYPES["ADMIN_COUNTRY"]: country_service,
        CONTENT_TYPES["ADMIN_KITCHEN"]: kitchen_service,
    }

    if service := services.get(content_type):
        state_data = await state.get_data()
        admin_callback = state_data.get("admin_callback")

        await service.delete(item_id, callback.from_user.id)
        await callback.message.edit_text(
            text=text_service.get_text("successful_deleting", language_code)
        )

        new_callback = await modify_callback(callback, Action.NAV, content_type, page)
        await admin_callback(new_callback, language_code, make_send=True)
        await state.clear()

    await callback.answer()


@registry.register("edit_profile")
async def handle_edit_profile(callback: CallbackQuery, language_code: str, **kwargs):
    await callback.message.answer(
        text_service.get_text("update_profile_instruction", language_code)
    )
    await callback.answer()


for content_type in [
    CONTENT_TYPES["ADMIN_COMPANY"],
    CONTENT_TYPES["ADMIN_COUNTRY"],
    CONTENT_TYPES["ADMIN_KITCHEN"],
    CONTENT_TYPES["COMPANY"],
    CONTENT_TYPES["PRODUCT"],
]:

    @registry.register(
        lambda data, ct=content_type: (
            json.loads(data).get("t") == ct and json.loads(data).get("a") == Action.NAV
        )
    )
    async def navigation_handler(callback: CallbackQuery, language_code: str, **kwargs):
        data = json.loads(callback.data)
        await handle_navigation(
            callback, language_code, data["t"], data.get("p", 1), **kwargs
        )


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
