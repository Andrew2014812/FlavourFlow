import json
from typing import Tuple

from aiohttp import ClientSession, ClientResponse

from bot.config import API_BASE_URL

texts = {}


def load_texts_from_json(file_path: str):
    global texts
    with open(file_path, encoding='utf-8') as file:
        data: dict = json.load(file)
        buttons = data.get("buttons", {})
        language_buttons = data.get("language_buttons", [])
        texts = data.get("texts", {})

    return buttons, language_buttons


def get_text(key: str, language: str):
    return texts.get(language, {}).get(key, "")


async def make_request(sub_url: str, data, method: str) -> Tuple[int, dict]:
    async with ClientSession() as session:
        method_func = getattr(session, method)

        url = f"{API_BASE_URL}/{sub_url}"

        async with method_func(url, json=data) as response:
            return response.status, await response.json()
