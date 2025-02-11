import os

from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)
texts_json_path = os.path.join(current_dir, 'texts.json')

dotenv_path = os.path.join(current_dir, '..', 'dev.env')
load_dotenv(dotenv_path=dotenv_path)


def get_env_variable(var_name: str, default_var_name: str = None) -> str:
    value = os.environ.get(var_name, default_var_name)
    if value is None:
        raise RuntimeError(f"The environment variable '{var_name}' is not set.")
    return value


TG_TOKEN = get_env_variable("TG_TOKEN")
GROUP_ID = get_env_variable("GROUP_ID")
ADMIN_ID = get_env_variable("ADMIN_ID")
ADMIN2_ID = get_env_variable("ADMIN2_ID")
db_name = get_env_variable("DB_NAME")
db_user = get_env_variable("DB_USER")
db_password = get_env_variable("DB_PASSWORD")
db_host = get_env_variable("DB_HOST")
db_port = get_env_variable("DB_PORT")
CLOUDINARY_CLOUD_NAME = get_env_variable("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = get_env_variable("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_env_variable("CLOUDINARY_API_SECRET")
JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
ALGORITHM = get_env_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES")
