from typing import Optional, Tuple

from aiogram import Dispatcher, Router
from aiogram.types import Message, PhotoSize

from bot.common.services.user_info_service import get_user_info
from bot.common.utils import make_request
from bot.config import APIAuth
from bot.handlers.entity_handlers.util import build_item_buttons

router = Router()


def render_company_content(
    page: int, language_code: str, category: str
) -> Tuple[str, Optional[str], int]:
    total_pages = 15
    image_url = (
        "https://i.pinimg.com/736x/bd/e5/64/bde56448f3661d1ea72631c07e400338.jpg"
    )

    caption = f"Company listing ({category}) - Page {page} of {total_pages} (lang: {language_code})"
    return caption, image_url, total_pages, None


def render_company_content_for_admin(page: int, language_code: str) -> Tuple:
    total_pages = 15
    companies = ["Tesla", "SpaceX", "Netflix", "Spotify", "Adobe", "Nvidia"]
    text = f"Company listing - Page {page} of {total_pages} (lang: {language_code})"
    builder = build_item_buttons(companies, "company", page)

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
