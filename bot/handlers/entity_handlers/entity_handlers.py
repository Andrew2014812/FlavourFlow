import json

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, PhotoSize
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...common.services.company_service import company_service
from ...common.services.gastronomy_service import country_service, kitchen_service
from ...common.services.text_service import text_service
from ..pagination_handlers import send_paginated_message
from .handler_utils import (
    ActionType,
    convert_raw_text_to_valid_dict,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_item_admin_details_keyboard,
)

router = Router()


class Form(StatesGroup):
    process_company = State()
    process_country = State()
    process_kitchen = State()
    confirm_delete = State()
    select_countries = State()
    select_kitchens = State()
    upload_image = State()


COMPANY_FIELD_MAPPING = {
    "Title ua:": "title_ua",
    "Title en:": "title_en",
    "Description ua:": "description_ua",
    "Description en:": "description_en",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
    "Опис ua:": "description_ua",
    "Опис en:": "description_en",
}

COUNTRY_KITCHEN_FIELD_MAPPING = {
    "Title ua:": "title_ua",
    "Title en:": "title_en",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
}

SERVICES = {
    "company": company_service,
    "country": country_service,
    "kitchen": kitchen_service,
}


async def render_details(
    message: Message, entity_type: str, item_id: int, page: int, language_code: str
):
    service = SERVICES[entity_type]
    item = await service.get_item(item_id)
    text = f"Title ua: {item.title_ua}\nTitle en: {item.title_en}"
    keyboard = get_item_admin_details_keyboard(
        f"admin-{entity_type}", page, language_code, item_id
    )
    await message.edit_text(text, reply_markup=keyboard)


async def initiate_action(
    callback: CallbackQuery,
    entity_type: str,
    action: ActionType,
    page: int,
    language_code: str,
    state: FSMContext,
    item_id: int = None,
):
    if action == ActionType.DELETE:
        text = text_service.get_text("country-kitchen_delete_confirm", language_code)
        keyboard = get_confirm_keyboard(
            language_code, f"admin-{entity_type}", page, item_id
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.confirm_delete)
    else:
        key = (
            "company_add_instruction"
            if action == ActionType.ADD
            else "company_edit_instruction"
        )
        if entity_type != "company":
            key = key.replace("company", "country-kitchen")
        text = text_service.get_text(key, language_code)
        keyboard = get_cancel_keyboard(language_code, f"admin-{entity_type}", page)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(getattr(Form, f"process_{entity_type}"))

    await state.update_data(
        entity_type=entity_type,
        language_code=language_code,
        page=page,
        action=action.value,
        item_id=item_id,
    )


async def get_countries_keyboard(language_code: str):
    countries = await country_service.get_list(page=1)
    builder = InlineKeyboardBuilder()

    for country in countries.countrys:
        title = country.title_ua if language_code == "ua" else country.title_en
        callback_data = json.dumps(
            {"t": "select_country", "id": country.id, "a": "select"},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=title, callback_data=callback_data))

    builder.adjust(1)
    return builder.as_markup()


async def get_kitchens_keyboard(language_code: str):
    kitchens = await kitchen_service.get_list(page=1)
    builder = InlineKeyboardBuilder()

    for kitchen in kitchens.kitchens:
        title = kitchen.title_ua if language_code == "ua" else kitchen.title_en
        callback_data = json.dumps(
            {"t": "select_kitchen", "id": kitchen.id, "a": "select"},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=title, callback_data=callback_data))

    builder.adjust(1)
    return builder.as_markup()


async def process_action(message: Message, state: FSMContext, entity_type: str):
    from ..pagination_handlers import send_paginated_message

    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    action = ActionType(data["action"])
    item_id = data.get("item_id")
    service = SERVICES[entity_type]

    field_mapping = (
        COMPANY_FIELD_MAPPING
        if entity_type == "company"
        else COUNTRY_KITCHEN_FIELD_MAPPING
    )

    is_allow_empty = action == ActionType.EDIT
    result = await convert_raw_text_to_valid_dict(
        message.text, field_mapping, is_allow_empty
    )

    if result.get("error"):
        await message.answer(text_service.get_text(result["error"], language_code))
        await state.clear()
        return

    if entity_type == "company" and action == ActionType.ADD:
        await state.update_data(company_data=result)
        await message.answer(
            text_service.get_text("select_countries", language_code),
            reply_markup=await get_countries_keyboard(language_code),
        )
        await state.set_state(Form.select_countries)

    else:
        if action == ActionType.ADD:
            await service.create(result, message.from_user.id)
            await message.answer(
                text_service.get_text("successful_adding", language_code)
            )

        elif action == ActionType.EDIT:
            await service.update(item_id, result, message.from_user.id)
            await message.answer(
                text_service.get_text("successful_editing", language_code)
            )

        await message.delete()
        await send_paginated_message(
            message, f"admin-{entity_type}", page, language_code
        )
        await state.clear()


async def process_country_selection(
    callback: CallbackQuery,
    state: FSMContext,
    item_id: int,
):
    language_code = (await state.get_data())["language_code"]

    await state.update_data(country_id=item_id)
    await callback.message.edit_text(
        text_service.get_text("select_kitchens", language_code),
        reply_markup=await get_kitchens_keyboard(language_code),
    )
    await state.set_state(Form.select_kitchens)

    await callback.answer()


async def process_kitchen_selection(
    callback: CallbackQuery, state: FSMContext, item_id: int
):
    language_code = (await state.get_data())["language_code"]

    await state.update_data(kitchen_id=item_id)
    await callback.message.edit_text(
        text_service.get_text("upload_company_image", language_code)
    )
    await state.set_state(Form.upload_image)

    await callback.answer()


@router.message(Form.upload_image)
async def process_image_upload(message: Message, state: FSMContext):
    state_data = await state.get_data()
    language_code = state_data["language_code"]
    page = state_data["page"]
    company_data = state_data["company_data"]
    country_id = str(state_data.get("country_id"))
    kitchen_id = str(state_data.get("kitchen_id"))

    if message.photo:
        photo: PhotoSize = message.photo[-1]
        file_id = photo.file_id

    elif message.sticker:
        file_id = message.sticker.file_id

    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    downloaded_file = await message.bot.download_file(file_path)
    image_bytes = downloaded_file.read()

    data = {
        **company_data,
        "country_id": country_id,
        "kitchen_id": kitchen_id,
        "image": image_bytes,
    }

    await company_service.create(data, message.from_user.id)
    await message.answer(text_service.get_text("successful_adding", language_code))

    await message.delete()

    await send_paginated_message(message, "admin-company", page, language_code)
    await state.clear()


@router.message(Form.process_company)
async def process_company_submission(message: Message, state: FSMContext):
    await process_action(message, state, "company")


@router.message(Form.process_country)
async def process_country_submission(message: Message, state: FSMContext):
    await process_action(message, state, "country")


@router.message(Form.process_kitchen)
async def process_kitchen_submission(message: Message, state: FSMContext):
    await process_action(message, state, "kitchen")


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
