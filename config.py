from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "bot.sqlite3"


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Заполните переменную {name} в файле .env")
    return value


def _username(name: str) -> str:
    return _required(name).removeprefix("@").strip()


def _boolean(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"Переменная {name} должна иметь значение true или false")


def _price(name: str) -> Decimal:
    value = _required(name).replace(",", ".")
    try:
        price = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Переменная {name} должна содержать число") from error
    if price < 0:
        raise ValueError(f"Переменная {name} не может быть отрицательной")
    return price


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    seller_username: str
    channel_url: str
    support_username: str
    product_name: str
    product_price: Decimal
    product_available: bool


def load_config() -> Config:
    # загружаем настройки из локального файла .env
    load_dotenv(BASE_DIR / ".env")
    return Config(
        bot_token=_required("BOT_TOKEN"),
        seller_username=_username("SELLER_USERNAME"),
        channel_url=_required("CHANNEL_URL"),
        support_username=_username("SUPPORT_USERNAME"),
        product_name=_required("PRODUCT_NAME"),
        product_price=_price("PRODUCT_PRICE"),
        product_available=_boolean("PRODUCT_AVAILABLE", default=True),
    )

