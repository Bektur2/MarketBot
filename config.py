from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    channel_url: str
    support_username: str
    admin_id: int | None


def load_config() -> Config:
    # загружаем настройки из локального файла .env
    load_dotenv(BASE_DIR / ".env")
    return Config(
        bot_token=_required("BOT_TOKEN"),
        channel_url=_required("CHANNEL_URL"),
        support_username=_username("SUPPORT_USERNAME"),
        admin_id=int(os.environ["ADMIN_ID"]) if os.getenv("ADMIN_ID", "").strip() else None,
    )
