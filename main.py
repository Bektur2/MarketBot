import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

from config import DATABASE_PATH, load_config
from database import Database
from handlers import get_main_router


async def main() -> None:
    # загружаем настройки и подготавливаем базу данных
    config = load_config()
    database = Database(DATABASE_PATH)
    await database.create_tables()

    # передаём настройки и базу данных во все обработчики
    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher(database=database, config=config)
    dispatcher.include_router(get_main_router())

    try:
        while True:
            try:
                await bot.me()
                break
            except TelegramNetworkError:
                logging.warning("Нет соединения с Telegram. Повтор подключения через 5 секунд. Остановить: Ctrl+C")
                await asyncio.sleep(5)
        # запускаем получение сообщений от telegram
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

