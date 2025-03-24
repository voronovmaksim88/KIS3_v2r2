# auth/utils.py
from datetime import datetime, timedelta, UTC

import bcrypt
import jwt

from core.config import settings


# Функция, которая создаёт jwt токен
def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)  # используем datetime.now(UTC)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode()  # Возвращаем строку вместо bytes


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode(), hashed_password=hashed.encode()
    )  # Преобразуем строку в bytes
