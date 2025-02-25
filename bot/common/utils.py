from typing import Dict

from aiohttp import ClientSession

from bot.config import API_BASE_URL, texts


def get_text(key: str, language: str):
    return texts.get(language, {}).get(key, "")


async def make_request(
        sub_url: str,
        method: str,
        body: Dict = None,
        data: Dict = None,
        params: Dict = None,
        headers: Dict = None,
) -> Dict:
    async with ClientSession() as session:
        url = f"{API_BASE_URL}/{sub_url}"

        try:
            async with session.request(
                    method=method, url=url, json=body, data=data, params=params, headers=headers
            ) as response:
                status_code = response.status
                data = await response.json()

                if status_code >= 400:
                    raise Exception(f"API error: {status_code} - {data}")

                return {"status": status_code, "data": data}

        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
