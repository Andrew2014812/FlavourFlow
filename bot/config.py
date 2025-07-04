import os
from enum import Enum

from aiogram import Bot
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
texts_json_path = os.path.join(current_dir, "texts.json")

dotenv_path = os.path.join(current_dir, "..", ".env")
sqlite_path = os.path.join(current_dir, "properties", "bot.db")
load_dotenv(dotenv_path=dotenv_path)


def get_env_variable(var_name: str, default_var_name: str = None) -> str:
    value = os.environ.get(var_name, default_var_name)
    if value is None:
        raise RuntimeError(f"The environment variable '{var_name}' is not set.")

    return value


async def get_bot() -> Bot:
    return Bot(token=TG_TOKEN)


class APIMethods(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class APIAuth(Enum):
    AUTH = "Authorization"


TG_TOKEN = get_env_variable("TG_TOKEN")
GROUP_ID = get_env_variable("GROUP_ID")
ADMIN_ID = get_env_variable("ADMIN_ID")
ADMIN2_ID = get_env_variable("ADMIN2_ID")
PG_DB_NAME = get_env_variable("DB_NAME")
PG_DB_USER = get_env_variable("DB_USER")
PG_DB_PASSWORD = get_env_variable("DB_PASSWORD")
PG_DB_HOST = get_env_variable("DB_HOST")
PG_DB_PORT = get_env_variable("DB_PORT")
CLOUDINARY_CLOUD_NAME = get_env_variable("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = get_env_variable("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_env_variable("CLOUDINARY_API_SECRET")
JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
JWT_ALGORITHM = get_env_variable("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES")
API_BASE_URL = get_env_variable("API_BASE_URL")
PAYMENTS_TOKEN = get_env_variable("PAYMENTS_TOKEN")
