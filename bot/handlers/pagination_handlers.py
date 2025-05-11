import json

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from ..common.services.gastronomy_service import kitchen_service
from ..common.services.text_service import text_service
from .entity_handlers.render_utils import (
    render_admin_list,
    render_company_list,
    render_product_list,
    render_user_cart_product,
    render_user_product_list,
)

ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"
DOT_MIDDLE = "🔘"
ARROW_BACK = "↩️"


def make_callback_data(
    content_type: str, action: str, page: int, extra_arg: str = "", kitchen_id: str = ""
):
    data = {"t": content_type, "a": action, "p": page}
    if extra_arg:
        data["e"] = extra_arg
    if kitchen_id:
        data["k"] = kitchen_id
    return json.dumps(data, separators=(",", ":"))


def build_pagination_keyboard(
    current_page: int,
    total_pages: int,
    content_type: str,
    extra_arg: str = "",
    kitchen_id: str = "",
    with_back_button: bool = True,
):
    buttons = []
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text=ARROW_LEFT,
                callback_data=make_callback_data(
                    content_type, "nav", current_page - 1, extra_arg, kitchen_id
                ),
            )
        )

    if total_pages <= 5:
        for page in range(1, total_pages + 1):
            text = f"[{page}]" if page == current_page else str(page)
            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=make_callback_data(
                        content_type, "nav", page, extra_arg, kitchen_id
                    ),
                )
            )
    else:
        if current_page <= 3:
            pages = [1, 2, 3, "...", total_pages - 1, total_pages]
        elif current_page >= total_pages - 2:
            pages = [1, "...", total_pages - 2, total_pages - 1, total_pages]
        else:
            pages = [1, "...", current_page, "...", total_pages]
        for page in pages:
            if page == "...":
                middle_page = total_pages // 2
                buttons.append(
                    InlineKeyboardButton(
                        text=DOT_MIDDLE,
                        callback_data=make_callback_data(
                            content_type, "nav", middle_page, extra_arg, kitchen_id
                        ),
                    )
                )
            else:
                text = f"[{page}]" if page == current_page else str(page)
                buttons.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=make_callback_data(
                            content_type, "nav", page, extra_arg, kitchen_id
                        ),
                    )
                )

    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text=ARROW_RIGHT,
                callback_data=make_callback_data(
                    content_type, "nav", current_page + 1, extra_arg, kitchen_id
                ),
            )
        )

    if with_back_button and content_type != "cart":
        back_button = InlineKeyboardButton(
            text=ARROW_BACK,
            callback_data=make_callback_data(
                content_type, "back", current_page, extra_arg, kitchen_id
            ),
        )
        return InlineKeyboardMarkup(inline_keyboard=[buttons, [back_button]])

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def update_paginated_message(
    callback: CallbackQuery,
    content_type: str,
    page: int,
    language_code: str,
    extra_arg: str = "",
    kitchen_id: str = "",
    with_back_button: bool = True,
):
    content = await get_content(
        content_type, page, language_code, extra_arg, kitchen_id
    )
    if not content:
        await callback.answer("Content not available")
        return

    caption, image_url, total_pages, builder = content
    if page > total_pages:
        page = max(1, total_pages)

    effective_with_back_button = with_back_button and content_type != "cart"

    keyboard = build_pagination_keyboard(
        page,
        total_pages,
        content_type,
        extra_arg,
        kitchen_id,
        effective_with_back_button,
    )

    merged_builder = InlineKeyboardBuilder()
    if builder:
        for button in builder.buttons:
            merged_builder.add(button)
    for row in keyboard.inline_keyboard:
        merged_builder.row(*row)
    reply_markup = merged_builder.as_markup()

    # Проверяем, является ли сообщение медиа (фото) или текстом
    is_media_content = image_url and content_type in [
        "user-company",
        "user-products",
        "cart",
    ]

    if is_media_content:
        try:
            await callback.message.edit_media(
                InputMediaPhoto(media=image_url, caption=caption),
                reply_markup=reply_markup,
            )
        except TelegramBadRequest as e:
            # Если редактирование медиа не удалось, отправляем новое сообщение
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=image_url, caption=caption, reply_markup=reply_markup
            )
    else:
        # Проверяем, содержит ли сообщение текст
        if callback.message.text or callback.message.caption:
            try:
                await callback.message.edit_text(caption, reply_markup=reply_markup)
            except TelegramBadRequest as e:
                # Если редактирование текста не удалось, отправляем новое сообщение
                await callback.message.delete()
                await callback.message.answer(caption, reply_markup=reply_markup)
        else:
            # Если сообщение не текст и не медиа, отправляем новое
            await callback.message.delete()
            await callback.message.answer(caption, reply_markup=reply_markup)


async def send_paginated_message(
    message: Message,
    content_type: str,
    page: int,
    language_code: str,
    extra_arg: str = "",
    kitchen_id: str = "",
    with_back_button: bool = True,
):
    content = await get_content(
        content_type, page, language_code, extra_arg, kitchen_id
    )
    if not content:
        await message.answer("Content not available")
        return

    caption, image_url, total_pages, builder = content
    if page > total_pages:
        page = max(1, total_pages)

    effective_with_back_button = with_back_button and content_type != "cart"

    keyboard = build_pagination_keyboard(
        page,
        total_pages,
        content_type,
        extra_arg,
        kitchen_id,
        effective_with_back_button,
    )

    merged_builder = InlineKeyboardBuilder()
    if builder:
        for button in builder.buttons:
            merged_builder.add(button)
    for row in keyboard.inline_keyboard:
        merged_builder.row(*row)
    reply_markup = merged_builder.as_markup()

    if image_url and content_type in ["user-company", "user-products", "cart"]:
        await message.answer_photo(
            photo=image_url, caption=caption, reply_markup=reply_markup
        )
    else:
        await message.answer(caption, reply_markup=reply_markup)


async def get_content(
    content_type: str,
    page: int,
    language_code: str,
    extra_arg: str = "",
    kitchen_id: str = "",
):
    if content_type == "user-company":
        return await render_company_list(page, language_code, kitchen_id, extra_arg)
    elif content_type in ["admin-company", "admin-country", "admin-kitchen"]:
        entity_type = content_type.replace("admin-", "")
        return await render_admin_list(entity_type, page, language_code)
    elif content_type == "admin-product":
        return await render_product_list(page, language_code, extra_arg)
    elif content_type == "user-products":
        return await render_user_product_list(page, language_code, extra_arg)
    elif content_type == "cart":
        return await render_user_cart_product(page, language_code, extra_arg)
    return None


async def get_category_keyboard(language_code: str):
    kitchen_list = await kitchen_service.get_list(page=1)
    builder = ReplyKeyboardBuilder()

    for kitchen in kitchen_list.kitchens:
        title = kitchen.title_en if language_code == "en" else kitchen.title_ua
        builder.add(KeyboardButton(text=title))

    builder.add(KeyboardButton(text=text_service.buttons[language_code]["back"]))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
