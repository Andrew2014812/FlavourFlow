import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'dev.env')
load_dotenv(dotenv_path=dotenv_path)


def get_env_variable(var_name: str, default_var_name: str = None) -> str:
    value = os.environ.get(var_name, default_var_name)
    if value is None:
        raise RuntimeError(f"The environment variable '{var_name}' is not set.")
    return value


APP_KEY = get_env_variable("APP_KEY")
APP_SECRET = get_env_variable("APP_SECRET")
TG_TOKEN = get_env_variable("TG_TOKEN")
GROUP_ID = get_env_variable("GROUP_ID")
ADMIN_ID = get_env_variable("ADMIN_ID")
ADMIN2_ID = get_env_variable("ADMIN2_ID")
INITIALIZE_ENGINE = get_env_variable("INITIALIZE_ENGINE")
db_name = get_env_variable("DB_NAME")
db_user = get_env_variable("DB_USER")
db_password = get_env_variable("DB_PASSWORD")
db_host = get_env_variable("DB_HOST")
db_port = get_env_variable("DB_PORT")