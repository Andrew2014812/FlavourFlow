import json
from enum import Enum
from typing import Callable, Optional, Tuple

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api.app.gastronomy.schemas import CountryResponse, KitchenResponse

from ...common.services.gastronomy_service import (
    CountryListResponse,
    create_country,
    create_kitchen,
    get_country,
    get_country_list,
    get_kitchen,
    get_kitchen_list,
    update_country,
    update_kitchen,
)
from ...common.services.text_service import text_service
from .handler_utils import (
    build_admin_buttons,
    convert_raw_text_to_valid_dict,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_item_admin_details_keyboard,
)


class ActionType(Enum):
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"


class Form(StatesGroup):
    process_country = State()
    confirm_delete = State()
    process_kitchen = State()


router = Router()

FIELD_MAPPING = {
    "Title ua:": "title_ua",
    "Title en:": "title_en",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
}


async def render_admin_countries_content(
    page: int,
    language_code: str,
) -> Tuple:
    result = await get_country_list(page=page)
    country_list_response: CountryListResponse = result
    total_pages = country_list_response.total_pages

    country_dict = {
        country.id: f"{country.title_ua} / {country.title_en}"
        for country in country_list_response.countries
    }

    builder = await build_admin_buttons(
        country_dict,
        "admin-country",
        language_code,
        page,
    )

    text = f"Country listing - Page {page} of {total_pages} (lang: ua / en)"
    return text, None, total_pages, builder


async def render_admin_kitchens_content(
    page: int,
    language_code: str,
) -> Tuple:
    result = await get_kitchen_list(page=page)
    kitchen_list_response: CountryListResponse = result
    total_pages = kitchen_list_response.total_pages

    kitchen_dict = {
        kitchen.id: f"{kitchen.title_ua} / {kitchen.title_en}"
        for kitchen in kitchen_list_response.kitchens
    }

    builder = await build_admin_buttons(
        kitchen_dict,
        "admin-kitchen",
        language_code,
        page,
    )

    text = f"Kitchen listing - Page {page} of {total_pages} (lang: ua / en)"
    return text, None, total_pages, builder


async def render_country_details_content(
    message: Message,
    current_page: int,
    language_code: str,
    country_id: int,
) -> None:
    result = await get_country(country_id=country_id)
    country: CountryResponse = result

    await message.edit_text(
        text=f"Title ua: {country.title_ua}\nTitle en: {country.title_en}",
        reply_markup=get_item_admin_details_keyboard(
            content_type="admin-country",
            current_page=current_page,
            language_code=language_code,
            item_id=country.id,
        ),
    )


async def render_kitchen_details_content(
    message: Message,
    current_page: int,
    language_code: str,
    kitchen_id: int,
) -> None:
    result = await get_kitchen(kitchen_id=kitchen_id)
    kitchen: KitchenResponse = result

    await message.edit_text(
        text=f"Title ua: {kitchen.title_ua}\nTitle en: {kitchen.title_en}",
        reply_markup=get_item_admin_details_keyboard(
            content_type="admin-kitchen",
            current_page=current_page,
            language_code=language_code,
            item_id=kitchen.id,
        ),
    )


async def initiate_country_action(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    action: ActionType,
    page: int,
    admin_countries: Callable[[CallbackQuery, str, bool], None],
    country_id: Optional[int] = None,
) -> None:
    if action == ActionType.DELETE:
        text = text_service.get_text("country-kitchen_delete_confirm", language_code)
        keyboard = get_confirm_keyboard(
            language_code,
            "admin-country",
            page,
            country_id,
        )
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.update_data(
            language_code=language_code,
            admin_countries=admin_countries,
            callback=callback,
            page=page,
            action=action.value,
            country_id=country_id,
        )
        await state.set_state(Form.confirm_delete)

    else:
        instruction_key = (
            "country-kitchen_add_instruction"
            if action == ActionType.ADD
            else "country-kitchen_edit_instruction"
        )
        text = text_service.get_text(instruction_key, language_code)
        keyboard = get_cancel_keyboard(language_code, "admin-country", page)
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.update_data(
            language_code=language_code,
            admin_countries=admin_countries,
            callback=callback,
            page=page,
            action=action.value,
            country_id=country_id,
        )
        await state.set_state(Form.process_country)


async def initiate_kitchen_action(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    action: ActionType,
    page: int,
    admin_kitchens: Callable[[CallbackQuery, str, bool], None],
    kitchen_id: Optional[int] = None,
) -> None:
    if action == ActionType.DELETE:
        text = text_service.get_text("country-kitchen_delete_confirm", language_code)
        keyboard = get_confirm_keyboard(
            language_code,
            "admin-kitchen",
            page,
            kitchen_id,
        )
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.update_data(
            language_code=language_code,
            admin_kitchens=admin_kitchens,
            callback=callback,
            page=page,
            action=action.value,
            kitchen_id=kitchen_id,
        )
        await state.set_state(Form.confirm_delete)

    else:
        instruction_key = (
            "country-kitchen_add_instruction"
            if action == ActionType.ADD
            else "country-kitchen_edit_instruction"
        )
        text = text_service.get_text(instruction_key, language_code)
        keyboard = get_cancel_keyboard(language_code, "admin-kitchen", page)
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.update_data(
            language_code=language_code,
            admin_kitchens=admin_kitchens,
            callback=callback,
            page=page,
            action=action.value,
            kitchen_id=kitchen_id,
        )
        await state.set_state(Form.process_kitchen)


async def process_country_action(
    message: Message,
    state: FSMContext,
    action: ActionType,
    admin_countries: Callable[[CallbackQuery, str, bool], None],
    country_id: Optional[int] = None,
) -> None:
    state_data = await state.get_data()
    language_code = state_data.get("language_code")
    page = state_data.get("page")
    callback: CallbackQuery = state_data.get("callback")

    is_allow_empty = action == ActionType.EDIT
    result = await convert_raw_text_to_valid_dict(
        message.text,
        FIELD_MAPPING,
        is_allow_empty,
    )

    if not result.get("error"):
        if action == ActionType.ADD:
            await create_country(result, message.from_user.id)
            success_message = "successful_adding"

        elif action == ActionType.EDIT:
            await update_country(country_id, result, message.from_user.id)
            success_message = "successful_editing"

        await message.answer(text_service.get_text(success_message, language_code))

        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-country"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_countries(new_callback, language_code, make_send=True)

    else:
        await message.answer(text_service.get_text(result["error"], language_code))

    await state.clear()


async def process_kitchen_action(
    message: Message,
    state: FSMContext,
    action: ActionType,
    admin_kitchens: Callable[[CallbackQuery, str, bool], None],
    kitchen_id: Optional[int] = None,
) -> None:
    state_data = await state.get_data()
    language_code = state_data.get("language_code")
    page = state_data.get("page")
    callback: CallbackQuery = state_data.get("callback")

    is_allow_empty = action == ActionType.EDIT
    result = await convert_raw_text_to_valid_dict(
        message.text,
        FIELD_MAPPING,
        is_allow_empty,
    )

    if not result.get("error"):
        if action == ActionType.ADD:
            await create_kitchen(result, message.from_user.id)
            success_message = "successful_adding"

        elif action == ActionType.EDIT:
            await update_kitchen(kitchen_id, result, message.from_user.id)
            success_message = "successful_editing"

        await message.answer(text_service.get_text(success_message, language_code))

        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-kitchen"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_kitchens(new_callback, language_code, make_send=True)

    else:
        await message.answer(text_service.get_text(result["error"], language_code))

    await state.clear()


async def add_country(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_countries: Callable[[CallbackQuery, str, bool], None],
    page: int,
) -> None:
    await initiate_country_action(
        callback,
        language_code,
        state,
        ActionType.ADD,
        page,
        admin_countries,
    )


async def add_kitchen(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_kitchens: Callable[[CallbackQuery, str, bool], None],
    page: int,
) -> None:
    await initiate_kitchen_action(
        callback,
        language_code,
        state,
        ActionType.ADD,
        page,
        admin_kitchens,
    )


async def edit_country(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_countries: Callable[[CallbackQuery, str, bool], None],
    page: int,
    country_id: int,
) -> None:
    await initiate_country_action(
        callback,
        language_code,
        state,
        ActionType.EDIT,
        page,
        admin_countries,
        country_id,
    )


async def edit_kitchen(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_kitchens: Callable[[CallbackQuery, str, bool], None],
    page: int,
    kitchen_id: int,
) -> None:
    await initiate_kitchen_action(
        callback,
        language_code,
        state,
        ActionType.EDIT,
        page,
        admin_kitchens,
        kitchen_id,
    )


async def delete_country_action(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_countries: Callable[[CallbackQuery, str, bool], None],
    page: int,
    country_id: int,
) -> None:
    await initiate_country_action(
        callback,
        language_code,
        state,
        ActionType.DELETE,
        page,
        admin_countries,
        country_id,
    )


async def delete_kitchen_action(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_kitchens: Callable[[CallbackQuery, str, bool], None],
    page: int,
    kitchen_id: int,
) -> None:
    await initiate_kitchen_action(
        callback,
        language_code,
        state,
        ActionType.DELETE,
        page,
        admin_kitchens,
        kitchen_id,
    )


@router.message(Form.process_country)
async def process_country_submission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    action = ActionType(state_data.get("action", ActionType.ADD.value))
    admin_countries = state_data.get("admin_countries")
    country_id = state_data.get("country_id")

    await process_country_action(message, state, action, admin_countries, country_id)


@router.message(Form.process_kitchen)
async def process_kitchen_submission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    action = ActionType(state_data.get("action", ActionType.ADD.value))
    admin_kitchens = state_data.get("admin_kitchens")
    kitchen_id = state_data.get("kitchen_id")

    await process_kitchen_action(message, state, action, admin_kitchens, kitchen_id)


def register_category_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)
