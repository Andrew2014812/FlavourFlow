from typing import Dict

from aiohttp import ClientSession

from bot.config import API_BASE_URL, texts


def get_text(key: str, language: str):
    return texts.get(language, {}).get(key, "")


async def make_request(
        sub_url: str,
        method: str,
        body: Dict = None,
        params: Dict = None,
        headers: Dict = None,
) -> Dict:
    async with ClientSession() as session:
        method_func = getattr(session, method)

        url = f"{API_BASE_URL}/{sub_url}"

        async with method_func(url, json=body, params=params, headers=headers) as response:
            return {"status": response.status, "data": await response.json()}
