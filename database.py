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
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price TEXT NOT NULL,
                    available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1)),
                    payment_username TEXT NOT NULL
                )
            """)
            await connection.execute("CREATE TABLE IF NOT EXISTS admins (telegram_id INTEGER PRIMARY KEY)")
            await connection.execute("CREATE TABLE IF NOT EXISTS admin_owner (slot INTEGER PRIMARY KEY CHECK(slot = 1), telegram_id INTEGER NOT NULL)")
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


    async def get_products(self) -> list[dict]:
        async with aiosqlite.connect(self.path) as connection:
            connection.row_factory = aiosqlite.Row
            cursor = await connection.execute("SELECT * FROM products ORDER BY id")
            return [dict(row) for row in await cursor.fetchall()]

    async def add_product(self, name: str, price: str, payment_username: str) -> int:
        async with aiosqlite.connect(self.path) as connection:
            cursor = await connection.execute(
                "INSERT INTO products (name, price, payment_username) VALUES (?, ?, ?)",
                (name, price, payment_username),
            )
            await connection.commit()
            return cursor.lastrowid

    async def delete_product(self, product_id: int) -> bool:
        async with aiosqlite.connect(self.path) as connection:
            cursor = await connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
            await connection.commit()
            return cursor.rowcount > 0

    async def set_product(self, product_id: int, field: str, value: str | int) -> bool:
        if field not in {"name", "price", "available", "payment_username"}:
            raise ValueError("Неизвестное поле товара")
        async with aiosqlite.connect(self.path) as connection:
            cursor = await connection.execute(
                f"UPDATE products SET {field} = ? WHERE id = ?", (value, product_id)
            )
            await connection.commit()
            return cursor.rowcount > 0

    async def set_user(self, telegram_id: int, field: str, value: int) -> bool:
        if field not in {"balance", "purchases_count"}:
            raise ValueError("Неизвестное поле пользователя")
        async with aiosqlite.connect(self.path) as connection:
            cursor = await connection.execute(
                f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, telegram_id)
            )
            await connection.commit()
            return cursor.rowcount > 0

    async def is_admin(self, telegram_id: int, username: str | None, admin_id: int | None) -> bool:
        async with aiosqlite.connect(self.path) as connection:
            if username and username.lower() == "bekturatil":
                await connection.execute(
                    "INSERT OR IGNORE INTO admin_owner (slot, telegram_id) VALUES (1, ?)",
                    (telegram_id,),
                )
                await connection.execute(
                    "INSERT OR IGNORE INTO admins SELECT telegram_id FROM admin_owner WHERE slot = 1"
                )
                await connection.commit()
            cursor = await connection.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
            return telegram_id == admin_id or await cursor.fetchone() is not None

    async def add_admin(self, telegram_id: int) -> None:
        async with aiosqlite.connect(self.path) as connection:
            await connection.execute("INSERT OR IGNORE INTO admins VALUES (?)", (telegram_id,))
            await connection.commit()

    async def get_user_by_username(self, username: str) -> User | None:
        async with aiosqlite.connect(self.path) as connection:
            connection.row_factory = aiosqlite.Row
            cursor = await connection.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
            )
            rows = await cursor.fetchall()
        return User(**dict(rows[0])) if len(rows) == 1 else None
