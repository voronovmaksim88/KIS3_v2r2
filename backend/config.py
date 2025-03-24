# config.py
from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# путь к базе данных Sqlite
DB_PATH = os.path.join(os.path.dirname(__file__), "KIS2", "db_test.sqlite3")

BASE_DIR = Path(__file__).resolve().parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 525600  # 365 дней, т.е на год


class Settings(BaseSettings):
    api_v1_prefix: str = ""
    auth_jwt: AuthJWT = AuthJWT()


# Создаем экземпляр настроек
settings = Settings()
