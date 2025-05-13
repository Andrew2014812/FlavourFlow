import json
from typing import Optional, Tuple

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from api.app.cart.schemas import CartItemFullResponse
from api.app.product.schemas import ProductListResponse

from ...common.services.cart_service import get_cart_items
from ...common.services.company_service import company_service
from ...common.services.gastronomy_service import kitchen_service
from ...common.services.product_service import product_service
from ...common.services.text_service import text_service
from .handler_utils import build_admin_buttons

SERVICES = {
    "company": company_service,
    "kitchen": kitchen_service,
}


async def render_admin_list(
    entity_type: str, page: int, language_code: str
) -> Tuple[str, None, int, InlineKeyboardBuilder]:
    service = SERVICES[entity_type]
    result = await service.get_list(page)
    total_pages = result.total_pages
    items = getattr(result, f"{entity_type}s")
    items_dict = {item.id: f"{item.title_ua} / {item.title_en}" for item in items}

    builder = await build_admin_buttons(
        items_dict, f"admin-{entity_type}", language_code, page
    )
    text = f"{entity_type.capitalize()} - Page {page} of {total_pages}"
    return text, None, total_pages, builder


async def render_company_list(
    page: int, language_code: str, kitchen_id: str, company_id: str = None
) -> Tuple[str, Optional[str], int, InlineKeyboardBuilder]:

    if company_id and company_id.isdigit():
        company = await company_service.get_item(int(company_id))

        if not company:
            return "Company not found", None, 1, None

        result = type("Result", (), {"companys": [company], "total_pages": 1})()
        total_pages = 1

    else:
        result = await company_service.get_list(
            page=page, limit=1, kitchen_id=kitchen_id
        )
        total_pages = result.total_pages
        if not result.companys:
            return "No companies found", None, 1, None

    company = result.companys[0]
    if language_code == "ua":
        text = f"{company.title_ua}\n\n{company.description_ua}\n"
    else:
        text = f"{company.title_en}\n\n{company.description_en}\n"

    builder = InlineKeyboardBuilder()
    products_button_text = "Go to products" if language_code == "en" else "До Страв"
    builder.row(
        InlineKeyboardButton(
            text=products_button_text,
            callback_data=json.dumps(
                {
                    "a": "list",
                    "t": "user-products",
                    "p": 1,
                    "e": str(company.id),
                    "k": kitchen_id or "",
                    "cp": page,
                },
                separators=(",", ":"),
            ),
        )
    )

    return text, company.image_link, total_pages, builder


async def render_product_list(page: int, language_code: str, company_id: str):
    if not company_id or not company_id.isdigit():
        return (
            text_service.get_text("generic_error", language_code)
            + ": Invalid company ID",
            None,
            0,
            None,
        )

    try:
        result: ProductListResponse = await product_service.get_list(
            company_id=int(company_id), page=page, limit=6
        )
    except Exception:
        return None, None, 0, None

    builder = InlineKeyboardBuilder()
    caption = text_service.get_text("product_title", language_code)

    if not result or not result.products:
        add_text = text_service.get_text("add_product_button", language_code)
        builder.row(
            InlineKeyboardButton(
                text=add_text,
                callback_data=json.dumps(
                    {"a": "add", "t": "admin-product", "p": page, "e": company_id},
                    separators=(",", ":"),
                ),
            )
        )
        return caption, None, 1, builder

    names = {
        item.id: item.title_ua if language_code == "ua" else item.title_en
        for item in result.products
    }
    builder = await build_admin_buttons(
        names, "admin-product", language_code, page, extra_arg=company_id
    )
    total_pages = result.total_pages

    return caption, None, total_pages, builder


async def render_user_product_list(
    page: int, language_code: str, company_id: str
) -> Tuple[str, Optional[str], int, InlineKeyboardBuilder]:
    result: ProductListResponse = await product_service.get_list(
        company_id=int(company_id), page=page, limit=1
    )

    builder = InlineKeyboardBuilder()

    product = result.products[0]
    product_name = product.title_en if language_code == "en" else product.title_ua
    composition = (
        product.composition_en if language_code == "en" else product.composition_ua
    )
    price_name = "Price" if language_code == "en" else "Ціна"
    caption = f"{product_name}\n{price_name}: {product.price} {product.currency}\n\n{composition}"
    builder.row(
        InlineKeyboardButton(
            text="Add to Cart" if language_code == "en" else "Додати до кошика",
            callback_data=json.dumps(
                {
                    "a": "add_to_cart",
                    "t": "user-products",
                    "p": page,
                    "e": str(product.id),
                },
                separators=(",", ":"),
            ),
        ),
        # InlineKeyboardButton(
        #     text=(
        #         "Add to Wishlist"
        #         if language_code == "en"
        #         else "Додати до списку бажань"
        #     ),
        #     callback_data=json.dumps(
        #         {
        #             "a": "add_to_wishlist",
        #             "t": "user-products",
        #             "p": page,
        #             "e": str(product.id),
        #         },
        #         separators=(",", ":"),
        #     ),
        # ),
    )

    total_pages = result.total_pages
    return caption, product.image_link, total_pages, builder


async def render_user_cart_product(
    page: int, language_code: str, telegram_id: int
) -> Tuple[str, Optional[str], int, InlineKeyboardBuilder]:
    cart_item: CartItemFullResponse = await get_cart_items(
        telegram_id=telegram_id, page=page
    )

    if not cart_item:
        return (
            "Cart is empty" if language_code == "en" else "Кошик порожній",
            None,
            0,
            None,
        )

    builder = InlineKeyboardBuilder()

    product_name = (
        cart_item.product_title_en
        if language_code == "en"
        else cart_item.product_title_ua
    )
    composition = (
        cart_item.composition_en if language_code == "en" else cart_item.composition_ua
    )
    price_name = "Price" if language_code == "en" else "Ціна"
    quantity_name = "Quantity" if language_code == "en" else "Кількість"
    total_name = "Total" if language_code == "en" else "Всього"
    caption = f"{product_name}\n\n{composition}\n\n{price_name}: {cart_item.price} {cart_item.currency}\n{quantity_name}: {cart_item.quantity}\n{total_name}: {cart_item.price * cart_item.quantity} {cart_item.currency}"
    builder.row(
        InlineKeyboardButton(
            text="╋",
            callback_data=json.dumps(
                {
                    "a": "plus",
                    "t": "cart",
                    "p": page,
                    "id": str(cart_item.id),
                },
                separators=(",", ":"),
            ),
        ),
        InlineKeyboardButton(
            text=("–"),
            callback_data=json.dumps(
                {
                    "a": "minus",
                    "t": "cart",
                    "p": page,
                    "id": str(cart_item.id),
                },
                separators=(",", ":"),
            ),
        ),
        InlineKeyboardButton(
            text=("Remove"),
            callback_data=json.dumps(
                {
                    "a": "remove",
                    "t": "cart",
                    "p": page,
                    "id": str(cart_item.id),
                },
                separators=(",", ":"),
            ),
        ),
    )

    total_pages = cart_item.total_pages
    return caption, cart_item.image_link, total_pages, builder
