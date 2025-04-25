from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ...common.services.company_service import company_service
from ...common.services.gastronomy_service import country_service, kitchen_service
from ...common.services.text_service import text_service
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

# Сервисы для разных сущностей
SERVICES = {
    "company": company_service,
    "country": country_service,
    "kitchen": kitchen_service,
}


# Отображение деталей элемента
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


# Инициировать действие (добавить, редактировать, удалить)
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


# Обработка ввода данных
async def process_action(message: Message, state: FSMContext, entity_type: str):
    from ..pagination_handlers import send_paginated_message  # Импорт внутри функции

    data = await state.get_data()
    language_code = data["language_code"]
    page = data["page"]
    action = ActionType(data["action"])
    item_id = data.get("item_id")
    service = SERVICES[entity_type]

    # Выбираем правильный маппинг в зависимости от типа сущности
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

    if action == ActionType.ADD:
        await service.create(result, message.from_user.id)
        await message.answer(text_service.get_text("successful_adding", language_code))
    elif action == ActionType.EDIT:
        await service.update(item_id, result, message.from_user.id)
        await message.answer(text_service.get_text("successful_editing", language_code))

    # Отправляем новое сообщение со списком
    await send_paginated_message(message, f"admin-{entity_type}", page, language_code)
    await state.clear()


# Хендлеры для обработки ввода
@router.message(Form.process_company)
async def process_company_submission(message: Message, state: FSMContext):
    await process_action(message, state, "company")


@router.message(Form.process_country)
async def process_country_submission(message: Message, state: FSMContext):
    await process_action(message, state, "country")


@router.message(Form.process_kitchen)
async def process_kitchen_submission(message: Message, state: FSMContext):
    await process_action(message, state, "kitchen")


# Регистрация хендлеров
def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
