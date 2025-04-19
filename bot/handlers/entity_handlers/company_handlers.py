import json
from typing import Callable, Optional, Tuple

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, PhotoSize

from ...common.services import text_service
from ...common.services.company_service import CompanyService
from ...common.services.text_service import text_service
from ...common.services.user_info_service import get_user_info
from ...common.utils import make_request
from ...config import APIAuth
from .handler_utils import (
    ActionType,
    build_admin_buttons,
    convert_raw_text_to_valid_dict,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_item_admin_details_keyboard,
)

router = Router()


class Form(StatesGroup):
    process_country = State()
    confirm_delete = State()
    process_kitchen = State()


FIELD_MAPPING = {
    "Title ua:": "title_ua",
    "Title en:": "title_en",
    "Description ua:": "description_ua",
    "Description en:": "description_en",
    "Назва ua:": "title_ua",
    "Назва en:": "title_en",
    "Опис ua:": "description_ua",
    "Опис en:": "description_en",
}


class CompanyHandler:
    def __init__(self, service: CompanyService, state_key: str):
        self.service = service
        self.state_key = state_key

    async def render_list_content(self, page: int, language_code: str) -> Tuple:
        result = await self.service.get_list(page)

        total_pages = result.total_pages
        items_dict = {
            item.id: f"{item.title_ua} / {item.title_en}"
            for item in getattr(result, f"{self.entity_type}s")
        }

        builder = await build_admin_buttons(
            items_dict, f"admin-{self.entity_type}", language_code, page
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


async def render_company_content(
    page: int, language_code: str, category: str
) -> Tuple[str, Optional[str], int]:
    total_pages = 15
    image_url = (
        "https://i.pinimg.com/736x/bd/e5/64/bde56448f3661d1ea72631c07e400338.jpg"
    )

    caption = f"Company listing ({category}) - Page {page} of {total_pages} (lang: {language_code})"
    return caption, image_url, total_pages, None


async def render_company_content_for_admin(
    page: int,
    language_code: str,
) -> Tuple:
    total_pages = 15
    companies = {
        1: "Tesla",
        2: "SpaceX",
        3: "Netflix",
        4: "Spotify",
        5: "Adobe",
        6: "Nvidia",
    }
    # companies = []
    text = f"Company listing - Page {page} of {total_pages} (lang: {language_code})"

    result = await build_admin_buttons(companies, "company", language_code, page)
    builder = result

    return text, None, total_pages, builder


# @router.message()
async def handle_image(message: Message):
    user_info = await get_user_info(message.from_user.id)

    if message.photo:
        photo: PhotoSize = message.photo[-1]
        file_id = photo.file_id

    elif message.sticker:
        file_id = message.sticker.file_id

    else:
        return

    file = await message.bot.get_file(file_id)
    file_path = file.file_path

    downloaded_file = await message.bot.download_file(file_path)
    image_bytes = downloaded_file.read()
    data = {
        "title_ua": "Testa",
        "title_en": "Testa",
        "description_ua": "Test",
        "description_en": "Test",
        "image": image_bytes,
        "kitchen_id": "1",
        "country_id": "1",
    }

    response = await make_request(
        "company/",
        "post",
        data=data,
        headers={
            APIAuth.AUTH.value: f"{user_info.token_type} {user_info.access_token}"
        },
    )
    print(response)


def register_company_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
