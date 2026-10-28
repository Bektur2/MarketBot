from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


@dataclass(frozen=True, slots=True)
class User:
    telegram_id: int
    username: str | None
    first_name: str
    balance: int
    purchases_count: int
    date_created: str


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    async def create_tables(self) -> None:
        # создаём таблицу пользователей при первом запуске
        async with aiosqlite.connect(self.path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
                    purchases_count INTEGER NOT NULL DEFAULT 0 CHECK (purchases_count >= 0),
                    date_created TEXT NOT NULL
                )
                """
            )
            await connection.commit()

    async def add_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str,
    ) -> None:
        # добавляем пользователя или обновляем его имя и username
        date_created = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.path) as connection:
            await connection.execute(
                """
                INSERT INTO users (telegram_id, username, first_name, date_created)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name
                """,
                (telegram_id, username, first_name, date_created),
            )
            await connection.commit()

    async def get_user(self, telegram_id: int) -> User | None:
        # получаем данные профиля по telegram id
        async with aiosqlite.connect(self.path) as connection:
            connection.row_factory = aiosqlite.Row
            cursor = await connection.execute(
                """
                SELECT telegram_id, username, first_name, balance,
                       purchases_count, date_created
                FROM users
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )
            row = await cursor.fetchone()

        return User(**dict(row)) if row else None

