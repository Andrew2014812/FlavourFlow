import json
from typing import Callable, Optional, Tuple

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from api.app.gastronomy.schemas import CountryResponse

from ...common.services.gastronomy_service import (
    CountryListResponse,
    create_country,
    get_country,
    get_country_list,
)
from ...common.services.text_service import text_service
from .handler_utils import (
    build_admin_buttons,
    convert_raw_text_to_valid_dict,
    get_item_admin_details_keyboard,
)


class Form(StatesGroup):
    proceed_add_country = State()


router = Router()


async def render_admin_countries_content(
    page: int,
    language_code: str,
) -> Tuple[str, Optional[str], int]:
    result = await get_country_list(page=page)
    country_list_response: CountryListResponse = result
    total_pages = country_list_response.total_pages

    country_dict = {
        country.id: f"{country.title_ua} / {country.title_en}"
        for country in country_list_response.countries
    }

    result = await build_admin_buttons(
        country_dict, "admin-country", language_code, page
    )
    builder = result

    text = f"Country listing - Page {page} of {total_pages} (lang: ua / en)"
    return text, None, total_pages, builder


async def render_country_details_content(
    message: Message,
    current_page: int,
    language_code: str,
    country_id: int,
) -> Tuple[str, Optional[str], int]:
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


async def add_country(
    callback: CallbackQuery,
    language_code: str,
    state: FSMContext,
    admin_countries: Callable,
    page: int,
):
    text = text_service.get_text("country-kitchen_add_instruction", language_code)

    message = callback.message
    await message.answer(text=text)

    await state.update_data(
        language_code=language_code,
        admin_countries=admin_countries,
        callback=callback,
        page=page,
    )
    await state.set_state(Form.proceed_add_country)


@router.message(Form.proceed_add_country)
async def proceed_add_country(message: Message, state: FSMContext):
    state_date = await state.get_data()
    language_code = state_date.get("language_code")
    admin_countries: Callable = state_date.get("admin_countries")
    callback: CallbackQuery = state_date.get("callback")
    page: int = state_date.get("page")

    field_mapping = {
        "Title ua:": "title_ua",
        "Title en:": "title_en",
        "Назва ua:": "title_ua",
        "Назва en:": "title_en",
    }

    result = await convert_raw_text_to_valid_dict(message.text, field_mapping)

    if not result.get("error"):
        await create_country(result, message.from_user.id)
        await message.answer(text_service.get_text("successful_adding", language_code))

        new_callback_data = json.dumps(
            {"a": "nav", "p": page, "t": "admin-country"}, separators=(",", ":")
        )
        new_callback = callback.model_copy(update={"data": new_callback_data})
        await admin_countries(new_callback, language_code, make_send=True)

    else:
        await message.answer(text_service.get_text(result["error"], language_code))

    await state.clear()


def register_category_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
