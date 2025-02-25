from aiogram import Router, Dispatcher
from aiogram.types import Message, PhotoSize

from bot.common.services.bot.user_info_service import get_user_info
from bot.common.utils import make_request
from bot.config import APIAuth

router = Router()


@router.message()
async def handle_image(message: Message):
    user_info = get_user_info(message.from_user.id)

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
        "country_id": "1"
    }

    response = await make_request("company/", "post", data=data,
                                  headers={APIAuth.AUTH.value: f'{user_info.token_type} {user_info.access_token}'}, )
    print(response)


def register_company_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
