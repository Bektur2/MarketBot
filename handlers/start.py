from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import Database
from keyboards.reply import main_menu_keyboard


router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, database: Database) -> None:
    if message.from_user is None:
        return

    # регистрируем пользователя перед показом главного меню
    await database.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.answer(
        "Добро пожаловать! Выберите нужный раздел.",
        reply_markup=main_menu_keyboard(),
    )

