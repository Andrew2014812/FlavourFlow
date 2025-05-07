import json
import logging

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, PhotoSize
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...common.services.product_service import product_service
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
    process_product = State()
    confirm_delete = State()
    edit_product_menu = State()
    edit_product_text = State()
    edit_product_image = State()
    upload_product_image = State()


PRODUCT_FIELD_MAPPING = {
    "Title ua:": "title_ua",
    "Title en:": "title_en",
    "Description ua:": "description_ua",
    "Description en:": "description_en",
    "Composition ua:": "composition_ua",
    "Composition en:": "composition_en",
    "Price:": "price",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
    "Опис ua:": "description_ua",
    "Опис en:": "description_en",
    "Склад ua:": "composition_ua",
    "Склад en:": "composition_en",
    "Ціна:": "price",
}


async def render_details(
    message: Message,
    item_id: int,
    page: int,
    language_code: str,
):
    item = await product_service.get_item(item_id)

    if isinstance(item, dict) and "error" in item:
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": {item['error']} (Status: {item['status_code']})"
        )
        await message.edit_text(error_text)
        return

    text = (
        f"Title ua: {item.title_ua}\n"
        f"Title en: {item.title_en}\n"
        f"Description ua: {item.description_ua}\n"
        f"Description en: {item.description_en}\n"
        f"Composition ua: {item.composition_ua}\n"
        f"Composition en: {item.composition_en}\n"
        f"Company id: {item.company_id}"
    )
    keyboard = get_item_admin_details_keyboard(
        "admin-product", page, language_code, item_id
    )
    await message.edit_text(text, reply_markup=keyboard)


async def get_edit_product_menu_keyboard(
    language_code: str, content_type: str, page: int, item_id: int
):
    builder = InlineKeyboardBuilder()
    buttons = [
        (
            "edit_product_text",
            "edit_text_button",
            "Змінити текст" if language_code == "ua" else "Edit text",
        ),
        (
            "edit_product_image",
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
    action: ActionType,
    page: int,
    language_code: str,
    state: FSMContext,
    company_id: int = None,
    item_id: int = None,
):

    if not company_id:
        product = await product_service.get_item(item_id)
        company_id = product.company_id

    await state.update_data(company_id=company_id)

    if action == ActionType.DELETE:
        text = text_service.get_text("product_delete_confirm", language_code)
        keyboard = get_confirm_keyboard(language_code, "admin-product", page, item_id)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.confirm_delete)

    elif action == ActionType.EDIT:
        text = text_service.get_text("select_edit_option", language_code)
        keyboard = await get_edit_product_menu_keyboard(
            language_code, "admin-product", page, item_id
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.edit_product_menu)

    else:
        text = text_service.get_text("product_add_instruction", language_code)
        keyboard = get_cancel_keyboard(language_code, "admin-product", page)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.process_product)

    await state.update_data(
        entity_type="product",
        language_code=language_code,
        page=page,
        action=action.value,
        item_id=item_id,
    )


async def process_action(message: Message, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    action = ActionType(data["action"])
    item_id = data.get("item_id")
    company_id = data["company_id"]

    logger.info(
        f"Processing action {action} for company_id={company_id}, message={message.text}"
    )

    is_allow_empty = action == ActionType.EDIT
    result = await convert_raw_text_to_valid_dict(
        message.text, PRODUCT_FIELD_MAPPING, is_allow_empty
    )

    if result.get("error"):
        error_text = (
            text_service.get_text("invalid_format", language_code)
            + "\n\n"
            + text_service.get_text("product_add_instruction", language_code)
        )
        await message.answer(error_text)
        return

    if action == ActionType.ADD:
        result["company_id"] = int(company_id)
        await state.update_data(product_data=result)
        await message.answer(
            text_service.get_text("upload_product_image", language_code)
        )
        await state.set_state(Form.upload_product_image)
        logger.info(
            f"Set state to Form.upload_product_image with product_data={result}"
        )
    else:
        response = await product_service.update(item_id, result, message.from_user.id)

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
        await send_paginated_message(
            message, "admin-product", page, language_code, extra_arg=str(company_id)
        )
        await state.clear()


async def process_edit_product_text(message: Message, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    item_id = data["item_id"]
    company_id = data["company_id"]

    result = await convert_raw_text_to_valid_dict(
        message.text, PRODUCT_FIELD_MAPPING, is_allow_empty=True
    )

    if result.get("error"):
        await message.answer(text_service.get_text(result["error"], language_code))
        return

    response = await product_service.update(item_id, result, message.from_user.id)

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
    await send_paginated_message(
        message, "admin-product", page, language_code, extra_arg=str(company_id)
    )
    await state.clear()


@router.message(Form.upload_product_image)
async def process_image_upload(message: Message, state: FSMContext):
    state_data = await state.get_data()
    language_code = state_data["language_code"]
    page = state_data["page"]
    product_data = state_data.get("product_data")
    item_id = state_data.get("item_id")
    company_id = str(state_data.get("company_id"))

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
    if product_data:
        data.update({**product_data})

    required_fields = [
        "title_ua",
        "title_en",
        "description_ua",
        "description_en",
        "composition_ua",
        "composition_en",
        "price",
    ]
    if product_data and not all(field in product_data for field in required_fields):
        missing_fields = [
            field for field in required_fields if field not in product_data
        ]
        error_text = (
            text_service.get_text("generic_error", language_code)
            + f": Missing required fields: {', '.join(missing_fields)}"
        )
        await message.answer(error_text)
        await state.clear()
        return

    response = (
        await product_service.create(data, image_bytes=image_bytes)
        if product_data
        else await product_service.update(item_id, data, message.from_user.id)
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
            "successful_adding" if product_data else "successful_editing", language_code
        )
    )
    await message.delete()
    await send_paginated_message(
        message,
        "admin-product",
        page,
        language_code,
        extra_arg=str(company_id),
    )
    await state.clear()


@router.message(Form.process_product)
async def process_product_submission(message: Message, state: FSMContext):
    await process_action(message, state)


@router.message(Form.edit_product_text)
async def process_product_text_submission(message: Message, state: FSMContext):
    await process_edit_product_text(message, state)


@router.message(Form.confirm_delete)
async def process_delete_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    item_id = data["item_id"]
    company_id = data["company_id"]

    response = await product_service.delete(item_id, callback.from_user.id)
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
        callback.message,
        "admin-product",
        page,
        language_code,
        extra_arg=str(company_id),
    )
    await state.clear()
    await callback.answer()


async def handle_edit_product_text(callback: CallbackQuery, state: FSMContext):
    data = json.loads(callback.data)
    language_code = (await state.get_data()).get("language_code", "en")
    page = data["p"]
    item_id = data["id"]

    await state.update_data(
        item_id=item_id,
        page=page,
        language_code=language_code,
    )

    text = text_service.get_text("product_edit_instruction", language_code)
    keyboard = get_cancel_keyboard(language_code, "admin-product", page)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(Form.edit_product_text)
    await callback.answer()


async def handle_edit_product_image(callback: CallbackQuery, state: FSMContext):
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
        text_service.get_text("upload_product_image", language_code)
    )
    await state.set_state(Form.upload_product_image)
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
