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
    "Product category:": "product_category",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
    "Опис ua:": "description_ua",
    "Опис en:": "description_en",
    "Склад ua:": "composition_ua",
    "Склад en:": "composition_en",
    "Категорія продукту:": "product_category",
}


async def render_details(
    message: Message,
    item_id: int,
    page: int,
    language_code: str,
    company_id: int,
    state: FSMContext,
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
        f"Product category: {item.product_category}\n"
        f"Company id: {item.company_id}"
    )
    keyboard = get_item_admin_details_keyboard(
        "admin-product", page, language_code, item_id
    )
    await message.edit_text(text, reply_markup=keyboard)
    await state.update_data(company_id=company_id)


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
    company_id: int,
    item_id: int = None,
):
    logger.info(
        f"Initiating action {action} for company_id={company_id}, item_id={item_id}"
    )
    await state.update_data(company_id=company_id)

    if action == ActionType.DELETE:
        text = text_service.get_text("product_delete_confirm", language_code)
        keyboard = get_confirm_keyboard(language_code, "admin-product", page, item_id)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.confirm_delete)
        logger.info(f"Set state to Form.confirm_delete for item_id={item_id}")

    elif action == ActionType.EDIT:
        text = text_service.get_text("select_edit_option", language_code)
        keyboard = await get_edit_product_menu_keyboard(
            language_code, "admin-product", page, item_id
        )
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.edit_product_menu)
        logger.info(f"Set state to Form.edit_product_menu for item_id={item_id}")

    else:  # ADD
        text = text_service.get_text("product_add_instruction", language_code)
        keyboard = get_cancel_keyboard(language_code, "admin-product", page)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(Form.process_product)
        logger.info(f"Set state to Form.process_product for company_id={company_id}")

    await state.update_data(
        entity_type="product",
        language_code=language_code,
        page=page,
        action=action.value,
        item_id=item_id,
    )
    logger.info(f"Updated state data: {await state.get_data()}")


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
        return  # Оставляем состояние для повторной попытки

    if action == ActionType.ADD:
        result["company_id"] = int(company_id)  # Преобразуем в int для API
        await state.update_data(product_data=result)
        await message.answer(
            text_service.get_text("upload_product_image", language_code)
        )
        await state.set_state(Form.upload_product_image)
        logger.info(
            f"Set state to Form.upload_product_image with product_data={result}"
        )
    else:  # EDIT
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
        "image": image_bytes,
    }

    await product_service.create(data, message.from_user.id)


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
