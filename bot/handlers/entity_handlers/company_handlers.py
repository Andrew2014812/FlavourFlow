from aiogram import Router, Dispatcher
from aiogram.types import (
    Message,
    PhotoSize,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from aiogram.filters import Command
from bot.common.services.user_info_service import get_user_info
from bot.common.utils import make_request
from bot.config import APIAuth
from bot.handlers.callback_handlers import register_callback_handler

router = Router()


class Company:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


def get_pagination_keyboard(
    current_page: int, total_pages: int
) -> InlineKeyboardMarkup:

    buttons = []

    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"page_{current_page - 1}"
            )
        )

    # Текущая страница
    buttons.append(
        InlineKeyboardButton(
            text=f"Страница {current_page}/{total_pages}",
            callback_data="current_page",
        )
    )

    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"page_{current_page + 1}"
            )
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard


@router.message(Command(commands=["companies"]))
async def companies_command(message: Message):
    companies = [Company(i, f"Компания {i}") for i in range(1, 25)]
    total_pages = 3
    current_page = 1

    # Формируем текст сообщения
    start_idx = (current_page - 1) * 10
    end_idx = start_idx + 10
    companies_text = "\n".join(
        f"{i + start_idx + 1}. {company.name}"
        for i, company in enumerate(companies[start_idx:end_idx])
    )

    # Отправляем сообщение с клавиатурой
    await message.answer(
        f"Список компаний:\n{companies_text}",
        reply_markup=get_pagination_keyboard(current_page, total_pages),
    )


@register_callback_handler(lambda callback: "page" in callback)
async def process_pagination(callback: CallbackQuery, language_code: str):
    if callback.data == "current_page":
        await callback.answer()
        return

    page = int(callback.data.split("_")[1])

    companies = [Company(i, f"Компания {i}") for i in range(1, 25)]
    total_pages = 3

    start_idx = (page - 1) * 10
    end_idx = start_idx + 10
    companies_text = "\n".join(
        f"{i + start_idx + 1}. {company.name}"
        for i, company in enumerate(companies[start_idx:end_idx])
    )

    # Обновляем сообщение
    await callback.message.edit_text(
        f"Список компаний:\n{companies_text}",
        reply_markup=get_pagination_keyboard(page, total_pages),
    )
    await callback.answer()


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
