import json
from typing import Callable, Union

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

callback_handlers = {}


def register_callback_handler(filter_arg: Union[str, Callable]):
    def decorator(func):
        if isinstance(filter_arg, str):
            filter_func = lambda data: data.startswith(filter_arg)
        else:
            filter_func = filter_arg

        callback_handlers[func] = filter_func
        return func

    return decorator


@router.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    user_info = await get_user_info(telegram_id)
    language_code = user_info.language_code

    for handler, filter_func in callback_handlers.items():
        try:
            if filter_func(callback.data):
                await handler(callback, language_code, state=state)
                return
        except json.JSONDecodeError:
            continue

    await callback.answer("Unknown action")


async def generic_admin_handler(handler: GenericGastronomyHandler):
    return create_pagination_handler(
        f"admin-{handler.entity_type}", handler.render_list_content
    )


async def handle_add(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    handler: GenericGastronomyHandler,
    page: int,
):
    await handler.initiate_action(
        callback,
        language_code,
        state,
        ActionType.ADD,
        page,
        generic_admin_handler(handler),
    )


async def handle_edit(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    handler: GenericGastronomyHandler,
    page: int,
    item_id: int,
):
    await handler.initiate_action(
        callback,
        language_code,
        state,
        ActionType.EDIT,
        page,
        generic_admin_handler(handler),
        item_id,
    )


async def handle_delete(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    handler: GenericGastronomyHandler,
    page: int,
    item_id: int,
):
    await handler.initiate_action(
        callback,
        language_code,
        state,
        ActionType.DELETE,
        page,
        generic_admin_handler(handler),
        item_id,
    )


async def handle_details(
    callback: CallbackQuery,
    language_code: str,
    handler: GenericGastronomyHandler,
    page: int,
    item_id: int,
):
    await handler.render_details_content(callback.message, page, language_code, item_id)


@register_callback_handler("edit_profile")
async def start_edit_profile(callback: CallbackQuery, language_code: str, **kwargs):
    await callback.message.answer(
        text_service.get_text("update_profile_instruction", language_code)
    )
    await callback.answer()


@register_callback_handler(
    lambda data: json.loads(data).get("t") == "admin-company"
    and json.loads(data).get("a") == "nav"
)
async def admin_companies(callback: CallbackQuery, language_code: str, **kwargs):
    await company_admin_handler(callback, language_code, **kwargs)


@register_callback_handler(
    lambda data: json.loads(data).get("t") == "admin-country"
    and json.loads(data).get("a") == "nav"
)
async def admin_countries(callback: CallbackQuery, language_code: str, **kwargs):
    await country_pagination_handler(callback, language_code, **kwargs)


@register_callback_handler(
    lambda data: json.loads(data).get("t") == "admin-kitchen"
    and json.loads(data).get("a") == "nav"
)
async def admin_kitchens(callback: CallbackQuery, language_code: str, **kwargs):
    await kitchen_pagination_handler(callback, language_code, **kwargs)


@register_callback_handler(
    lambda data: json.loads(data).get("t") == "user-company"
    and json.loads(data).get("a") == "nav"
)
async def company_pagination(callback: CallbackQuery, language_code: str, **kwargs):
    await company_handler(callback, language_code)


@register_callback_handler(
    lambda data: json.loads(data).get("t") == "product"
    and json.loads(data).get("a") == "nav"
)
async def product_pagination(callback: CallbackQuery, language_code: str, **kwargs):
    await product_handler(callback, language_code)


@register_callback_handler(lambda data: json.loads(data).get("t") == "category")
async def category_selection(callback: CallbackQuery, language_code: str, **kwargs):
    data = json.loads(callback.data)
    category = data["v"].capitalize()
    callback_dict = {"t": "user-company", "a": "nav", "p": 1, "e": category}
    new_callback_data = json.dumps(callback_dict, separators=(",", ":"))
    new_callback = callback.model_copy(update={"data": new_callback_data})
    await company_pagination(new_callback, language_code)


@register_callback_handler(lambda data: json.loads(data).get("a") == "back")
async def handle_back(callback: CallbackQuery, language_code: str, **kwargs):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]

    if content_type == "user-company":
        await callback.message.delete()
        await handle_restaurants(callback.message, language_code)
    elif content_type in ["admin-company", "admin-country", "admin-kitchen"]:
        await handle_admin(
            callback.message, language_code, telegram_id=callback.from_user.id
        )
    elif content_type == "admin-country-details":
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-country"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_countries(new_callback, language_code)
    elif content_type == "admin-kitchen-details":
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-kitchen"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_kitchens(new_callback, language_code)
    await callback.answer()


@register_callback_handler(lambda data: json.loads(data).get("a") == "add")
async def handle_add_action(
    callback: CallbackQuery, language_code: str, state: FSMContext, **kwargs
):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]

    if content_type == "admin-country":
        await handle_add(callback, language_code, state, country_handler, page)
    elif content_type == "admin-kitchen":
        await handle_add(callback, language_code, state, kitchen_handler, page)


@register_callback_handler(lambda data: json.loads(data).get("a") == "edit")
async def handle_edit_action(
    callback: CallbackQuery, language_code: str, state: FSMContext
):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]
    item_id = callback_data["id"]

    if content_type == "admin-country":
        await handle_edit(
            callback, language_code, state, country_handler, page, item_id
        )
    elif content_type == "admin-kitchen":
        await handle_edit(
            callback, language_code, state, kitchen_handler, page, item_id
        )


@register_callback_handler(lambda data: json.loads(data).get("a") == "details")
async def handle_item_details(callback: CallbackQuery, language_code: str, **kwargs):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]
    item_id = callback_data["id"]

    if content_type == "admin-country":
        await handle_details(callback, language_code, country_handler, page, item_id)
    elif content_type == "admin-kitchen":
        await handle_details(callback, language_code, kitchen_handler, page, item_id)
    await callback.answer()


@register_callback_handler(lambda data: json.loads(data).get("a") == "cancel")
async def handle_cancel(
    callback: CallbackQuery, language_code: str, state: FSMContext
) -> None:
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]
    await state.clear()

    if content_type == "admin-country":
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-country"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_countries(new_callback, language_code)
    elif content_type == "admin-kitchen":
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-kitchen"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_kitchens(new_callback, language_code)
    await callback.answer()


@register_callback_handler(lambda data: json.loads(data).get("a") == "delete")
async def handle_delete_action(
    callback: CallbackQuery, language_code: str, state: FSMContext, **kwargs
):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]
    item_id = callback_data["id"]

    if content_type == "admin-country":
        await handle_delete(
            callback, language_code, state, country_handler, page, item_id
        )
    elif content_type == "admin-kitchen":
        await handle_delete(
            callback, language_code, state, kitchen_handler, page, item_id
        )
    await callback.answer()


@register_callback_handler(lambda data: json.loads(data).get("a") == "confirm_delete")
async def handle_confirm_delete(
    callback: CallbackQuery, language_code: str, state: FSMContext, **kwargs
):
    callback_data = json.loads(callback.data)
    content_type = callback_data["t"]
    page = callback_data["p"]
    item_id = callback_data["id"]

    if content_type == "admin-country":
        state_data = await state.get_data()
        admin_countries_callable = await state_data.get("admin_callback")
        await country_service.delete(item_id, callback.from_user.id)
        await callback.message.edit_text(
            text=text_service.get_text("successful_deleting", language_code)
        )
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-country"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_countries_callable(new_callback, language_code, make_send=True)
        await state.clear()

    elif content_type == "admin-kitchen":
        state_data = await state.get_data()
        admin_kitchens_callable = await state_data.get("admin_callback")
        await kitchen_service.delete(item_id, callback.from_user.id)
        await callback.message.edit_text(
            text=text_service.get_text("successful_deleting", language_code)
        )
        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-kitchen"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_kitchens_callable(new_callback, language_code, make_send=True)

        await state.clear()

    await callback.answer()


def register_callback_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
