from aiogram import F, Router
from aiogram.types import Message

from database import Database
from keyboards.reply import PROFILE_BUTTON


router = Router(name="profile")


@router.message(F.text == PROFILE_BUTTON)
async def show_profile(message: Message, database: Database) -> None:
    if message.from_user is None:
        return

    # сохраняем актуальные данные пользователя перед выводом профиля
    await database.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    user = await database.get_user(message.from_user.id)
    if user is None:
        return

    # если username отсутствует, используем обычное имя
    display_name = user.username or user.first_name
    await message.answer(
        f"{display_name}\n"
        f"ID: {user.telegram_id}\n"
        f"Ваш баланс: {user.balance} ₽\n"
        f"Количество покупок: {user.purchases_count}"
    )

