from aiogram import F, Router
from aiogram.types import Message

router = Router(name="fallback")


@router.message(F.text, ~F.text.startswith("/"))
async def fallback(message: Message) -> None:
    await message.answer("Используйте кнопки меню")
