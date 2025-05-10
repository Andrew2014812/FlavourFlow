import json
import logging

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


class Form(StatesGroup):
    process_company = State()
    process_country = State()
    process_kitchen = State()
    confirm_delete = State()
    select_countries = State()
    select_kitchens = State()
    upload_image = State()
    edit_company_menu = State()
    edit_company_text = State()
    edit_company_country = State()
    edit_company_kitchen = State()
    edit_company_image = State()


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
    message: Message,
    entity_type: str,
    item_id: int,
    page: int,
    language_code: str,
):
    service = SERVICES[entity_type]
    item = await service.get_item(item_id)

    if isinstance(item, dict) and "error" in item:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {item['error']} (Status: {item['status_code']})"
        )
        await message.edit_text(error_text)
        return

    text = f"Title ua: {item.title_ua}\nTitle en: {item.title_en}"
    if entity_type == "company":
        text += f"\nDescription ua: {item.description_ua}\nDescription en: {item.description_en}"
    keyboard = get_item_admin_details_keyboard(
        f"admin-{entity_type}", page, language_code, item_id
    )
    await message.edit_text(text, reply_markup=keyboard)


async def get_edit_company_menu_keyboard(
    language_code: str, content_type: str, page: int, item_id: int
):
    builder = InlineKeyboardBuilder()
    buttons = [
        (
            "edit_company_text",
            "edit_text_button",
            "Змінити текст" if language_code == "ua" else "Edit text",
        ),
        (
            "edit_company_country",
            "edit_country_button",
            "Змінити країну" if language_code == "ua" else "Edit country",
        ),
        (
            "edit_company_kitchen",
            "edit_kitchen_button",
            "Змінити кухню" if language_code == "ua" else "Edit kitchen",
        ),
        (
            "edit_company_image",
            "edit_image_button",
            "Змінити зображення" if language_code == "ua" else "Edit image",
        ),
    ]

    for callback_type, text_key, button_text in buttons:
        callback_data = json.dumps(
            {"t": callback_type, "p": page, "id": item_id},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    cancel_data = json.dumps(
        {"t": content_type, "p": page, "a": "cancel"},
        separators=(",", ":"),
    )
    builder.add(
        InlineKeyboardButton(
            text=text_service.get_text("cancel_button", language_code),
            callback_data=cancel_data,
        )
    )

    builder.adjust(1)
    return builder.as_markup()


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

    elif action == ActionType.EDIT and entity_type == "company":
        text = text_service.get_text("select_edit_option", language_code)
        keyboard = await get_edit_company_menu_keyboard(
            language_code, f"admin-{entity_type}", page, item_id
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.edit_company_menu)

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


async def get_countries_keyboard(language_code: str, action: str = "create"):
    countries = await country_service.get_list(page=1)

    if isinstance(countries, dict) and "error" in countries:
        return None, countries["error"], countries["status_code"]

    builder = InlineKeyboardBuilder()

    callback_type = (
        "select_country_create" if action == "create" else "select_country_edit"
    )

    for country in countries.countrys:
        title = country.title_ua if language_code == "ua" else country.title_en
        callback_data = json.dumps(
            {"t": callback_type, "id": country.id, "a": "select"},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=title, callback_data=callback_data))

    builder.adjust(1)
    return builder.as_markup(), None, None


async def get_kitchens_keyboard(language_code: str, action: str = "create"):
    kitchens = await kitchen_service.get_list(page=1)

    if isinstance(kitchens, dict) and "error" in kitchens:
        return None, kitchens["error"], kitchens["status_code"]

    builder = InlineKeyboardBuilder()

    callback_type = (
        "select_kitchen_create" if action == "create" else "select_kitchen_edit"
    )

    for kitchen in kitchens.kitchens:
        title = kitchen.title_ua if language_code == "ua" else kitchen.title_en
        callback_data = json.dumps(
            {"t": callback_type, "id": kitchen.id, "a": "select"},
            separators=(",", ":"),
        )
        builder.add(InlineKeyboardButton(text=title, callback_data=callback_data))

    builder.adjust(1)
    return builder.as_markup(), None, None


async def process_action(message: Message, state: FSMContext, entity_type: str):
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
        keyboard, error, status_code = await get_countries_keyboard(
            language_code, action="create"
        )
        if error:
            error_text = (
                text_service.get_text("generic_error", language_code)
                + f": {error} (Status: {status_code})"
            )
            await message.answer(error_text)
            await state.clear()
            return

        await message.answer(
            text_service.get_text("select_countries", language_code),
            reply_markup=keyboard,
        )
        await state.set_state(Form.select_countries)

    else:
        if action == ActionType.ADD:
            response = await service.create(result, message.from_user.id)

            if isinstance(response, dict) and "error" in response:
                error_text = (
                    text_service.get_text("generic_error", language_code)
                    + f": {response['error']} (Status: {response['status_code']})"
                )
                await message.answer(error_text)
                await state.clear()
                return

            await message.answer(
                text_service.get_text("successful_adding", language_code)
            )

        elif action == ActionType.EDIT:
            response = await service.update(item_id, result, message.from_user.id)

            if isinstance(response, dict) and "error" in response:
                error_text = (
                    text_service.get_text("generic_error", language_code)
                    + f": {response['error']} (Status: {response['status_code']})"
                )
                await message.answer(error_text)
                await state.clear()
                return

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
    keyboard, error, status_code = await get_kitchens_keyboard(
        language_code, action="create"
    )

    if error:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {error} (Status: {status_code})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("select_kitchens", language_code),
        reply_markup=keyboard,
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


async def process_edit_company_text(message: Message, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    item_id = data["item_id"]

    result = await convert_raw_text_to_valid_dict(
        message.text, COMPANY_FIELD_MAPPING, is_allow_empty=True
    )

    if result.get("error"):
        await message.answer(text_service.get_text(result["error"], language_code))
        return

    response = await company_service.update(item_id, result, message.from_user.id)

    if isinstance(response, dict) and "error" in response:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {response['error']} (Status: {response['status_code']})"
        )
        await message.answer(error_text)
        await state.clear()
        return

    await message.answer(text_service.get_text("successful_editing", language_code))
    await message.delete()
    await send_paginated_message(message, "admin-company", page, language_code)
    await state.clear()


async def process_edit_company_country(
    callback: CallbackQuery, state: FSMContext, item_id: int
):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    company_id = data["item_id"]

    response = await company_service.update(
        company_id, {"country_id": str(item_id)}, callback.from_user.id
    )

    if isinstance(response, dict) and "error" in response:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {response['error']} (Status: {response['status_code']})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("successful_editing", language_code)
    )
    await send_paginated_message(callback.message, "admin-company", page, language_code)
    await state.clear()
    await callback.answer()


async def process_edit_company_kitchen(
    callback: CallbackQuery, state: FSMContext, item_id: int
):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    company_id = data["item_id"]

    response = await company_service.update(
        company_id, {"kitchen_id": str(item_id)}, callback.from_user.id
    )
    if isinstance(response, dict) and "error" in response:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {response['error']} (Status: {response['status_code']})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("successful_editing", language_code)
    )
    await send_paginated_message(callback.message, "admin-company", page, language_code)
    await state.clear()
    await callback.answer()


@router.message(Form.upload_image)
async def process_image_upload(message: Message, state: FSMContext):
    state_data = await state.get_data()
    language_code = state_data["language_code"]
    page = state_data["page"]
    company_data = state_data.get("company_data")
    country_id = str(state_data.get("country_id"))
    kitchen_id = str(state_data.get("kitchen_id"))
    item_id = state_data.get("item_id")

    if message.photo:
        photo: PhotoSize = message.photo[-1]
        file_id = photo.file_id

    elif message.sticker:
        file_id = message.sticker.file_id

    else:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + ": No valid image or sticker provided"
        )
        await message.answer(error_text)
        await state.clear()
        return

    try:
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await message.bot.download_file(file_path)
        image_bytes = downloaded_file.read()

    except Exception as e:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": Failed to download image - {str(e)}"
        )
        await message.answer(error_text)
        await state.clear()
        return

    data = {
        "image": image_bytes,
    }
    if company_data:
        data.update(
            {
                **company_data,
                "country_id": country_id,
                "kitchen_id": kitchen_id,
            }
        )

    response = (
        await company_service.create(data, message.from_user.id)
        if company_data
        else await company_service.update(item_id, data, message.from_user.id)
    )

    if isinstance(response, dict) and "error" in response:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {response['error']}"
        )
        await message.answer(error_text)
        await state.clear()
        return

    await message.answer(
        text_service.get_text(
            "successful_adding" if company_data else "successful_editing", language_code
        )
    )
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


@router.message(Form.edit_company_text)
async def process_company_text_submission(message: Message, state: FSMContext):
    await process_edit_company_text(message, state)


@router.callback_query(Form.confirm_delete)
async def process_delete_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    entity_type = data["entity_type"]
    item_id = data["item_id"]
    service = SERVICES[entity_type]

    response = await service.delete(item_id, callback.from_user.id)
    if isinstance(response, dict) and "error" in response:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {response['error']} (Status: {response['status_code']})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("successful_deleting", language_code)
    )
    await send_paginated_message(
        callback.message, f"admin-{entity_type}", page, language_code
    )
    await state.clear()
    await callback.answer()


async def handle_edit_company_text(callback: CallbackQuery, state: FSMContext):
    data = json.loads(callback.data)
    language_code = (await state.get_data()).get("language_code", "en")
    page = data["p"]
    item_id = data["id"]

    await state.update_data(
        item_id=item_id,
        page=page,
        language_code=language_code,
    )

    text = text_service.get_text("company_edit_instruction", language_code)
    keyboard = get_cancel_keyboard(language_code, "admin-company", page)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(Form.edit_company_text)
    await callback.answer()


async def handle_edit_company_country(callback: CallbackQuery, state: FSMContext):
    data = json.loads(callback.data)
    language_code = (await state.get_data()).get("language_code", "en")
    page = data["p"]
    item_id = data["id"]

    await state.update_data(
        item_id=item_id,
        page=page,
        language_code=language_code,
    )

    keyboard, error, status_code = await get_countries_keyboard(
        language_code, action="edit"
    )
    if error:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {error} (Status: {status_code})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("select_countries", language_code),
        reply_markup=keyboard,
    )
    await state.set_state(Form.edit_company_country)
    await callback.answer()


async def handle_edit_company_kitchen(callback: CallbackQuery, state: FSMContext):
    data = json.loads(callback.data)
    language_code = (await state.get_data()).get("language_code", "en")
    page = data["p"]
    item_id = data["id"]

    await state.update_data(
        item_id=item_id,
        page=page,
        language_code=language_code,
    )

    keyboard, error, status_code = await get_kitchens_keyboard(
        language_code, action="edit"
    )
    if error:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {error} (Status: {status_code})"
        )
        await callback.message.edit_text(error_text)
        await state.clear()
        return

    await callback.message.edit_text(
        text_service.get_text("select_kitchens", language_code),
        reply_markup=keyboard,
    )
    await state.set_state(Form.edit_company_kitchen)
    await callback.answer()


async def handle_edit_company_image(callback: CallbackQuery, state: FSMContext):
    data = json.loads(callback.data)
    language_code = (await state.get_data()).get("language_code", "en")
    page = data["p"]
    item_id = data["id"]

    await state.update_data(
        item_id=item_id,
        page=page,
        language_code=language_code,
    )

    await callback.message.edit_text(
        text_service.get_text("upload_company_image", language_code)
    )
    await state.set_state(Form.upload_image)
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
