import json
from typing import Callable, Optional, Tuple

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ...common.services.gastronomy_service import (
    GastronomyService,
    country_service,
    kitchen_service,
)
from ...common.services.text_service import text_service
from .handler_utils import (
    ActionType,
    build_admin_buttons,
    convert_raw_text_to_valid_dict,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_item_admin_details_keyboard,
)


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


class GenericGastronomyHandler:
    def __init__(self, entity_type: str, service: GastronomyService, state_key: str):
        self.entity_type = entity_type
        self.service = service
        self.state_key = state_key

    async def render_admin_list_content(self, page: int, language_code: str) -> Tuple:
        result = await self.service.get_list(page)
        total_pages = result.total_pages
        items_dict = {
            item.id: f"{item.title_ua} / {item.title_en}"
            for item in getattr(result, f"{self.entity_type}s")
        }
        builder = await build_admin_buttons(
            items_dict,
            f"admin-{self.entity_type}",
            language_code,
            page,
        )
        text = f"{self.entity_type.capitalize()} listing - Page {page} of {total_pages} (lang: ua / en)"
        return text, None, total_pages, builder

    async def render_details_content(
        self, message: Message, current_page: int, language_code: str, item_id: int
    ) -> None:
        item = await self.service.get_item(item_id)
        await message.edit_text(
            text=f"Title ua: {item.title_ua}\nTitle en: {item.title_en}",
            reply_markup=get_item_admin_details_keyboard(
                content_type=f"admin-{self.entity_type}",
                current_page=current_page,
                language_code=language_code,
                item_id=item.id,
            ),
        )

    async def initiate_action(
        self,
        callback: CallbackQuery,
        language_code: str,
        state: FSMContext,
        action: ActionType,
        page: int,
        admin_callback: Callable[[CallbackQuery, str, bool], None],
        item_id: Optional[int] = None,
    ) -> None:
        if action == ActionType.DELETE:
            text = text_service.get_text(
                "country-kitchen_delete_confirm", language_code
            )
            keyboard = get_confirm_keyboard(
                language_code, f"admin-{self.entity_type}", page, item_id
            )
            await callback.message.edit_text(text=text, reply_markup=keyboard)
            await state.update_data(
                language_code=language_code,
                admin_callback=admin_callback,
                callback=callback,
                page=page,
                action=action.value,
                item_id=item_id,
            )
            await state.set_state(Form.confirm_delete)
        else:
            instruction_key = (
                "country-kitchen_add_instruction"
                if action == ActionType.ADD
                else "country-kitchen_edit_instruction"
            )
            text = text_service.get_text(instruction_key, language_code)
            keyboard = get_cancel_keyboard(
                language_code, f"admin-{self.entity_type}", page
            )
            await callback.message.edit_text(text=text, reply_markup=keyboard)
            await state.update_data(
                language_code=language_code,
                admin_callback=admin_callback,
                callback=callback,
                page=page,
                action=action.value,
                item_id=item_id,
            )
            await state.set_state(getattr(Form, f"process_{self.entity_type}"))

    async def process_action(
        self,
        message: Message,
        state: FSMContext,
        action: ActionType,
        admin_callback: Callable[[CallbackQuery, str, bool], None],
        item_id: Optional[int] = None,
    ) -> None:
        state_data = await state.get_data()
        language_code = state_data.get("language_code")
        page = state_data.get("page")
        callback: CallbackQuery = state_data.get("callback")

        is_allow_empty = action == ActionType.EDIT
        result = await convert_raw_text_to_valid_dict(
            message.text, FIELD_MAPPING, is_allow_empty
        )

        if not result.get("error"):
            if action == ActionType.ADD:
                await self.service.create(result, message.from_user.id)
                success_message = "successful_adding"

            elif action == ActionType.EDIT:
                await self.service.update(item_id, result, message.from_user.id)
                success_message = "successful_editing"

            await message.answer(text_service.get_text(success_message, language_code))
            new_callback_data = json.dumps(
                {"a": "nav", "p": page, "t": f"admin-{self.entity_type}"},
                separators=(",", ":"),
            )
            new_callback = callback.model_copy(update={"data": new_callback_data})
            await admin_callback(new_callback, language_code, make_send=True)

        else:
            await message.answer(text_service.get_text(result["error"], language_code))

        await state.clear()


country_handler = GenericGastronomyHandler(
    "country", country_service, "process_country"
)
kitchen_handler = GenericGastronomyHandler(
    "kitchen", kitchen_service, "process_kitchen"
)


@router.message(Form.process_country)
async def process_country_submission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    action = ActionType(state_data.get("action", ActionType.ADD.value))
    admin_callback = state_data.get("admin_callback")
    item_id = state_data.get("item_id")

    await country_handler.process_action(
        message,
        state,
        action,
        admin_callback,
        item_id,
    )


@router.message(Form.process_kitchen)
async def process_kitchen_submission(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    action = ActionType(state_data.get("action", ActionType.ADD.value))
    admin_callback = state_data.get("admin_callback")
    item_id = state_data.get("item_id")
    await kitchen_handler.process_action(
        message,
        state,
        action,
        admin_callback,
        item_id,
    )


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
