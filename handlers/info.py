from aiogram import F, Router
from aiogram.types import Message

from config import Config
from keyboards.reply import INFO_BUTTON


router = Router(name="info")


@router.message(F.text == INFO_BUTTON)
async def show_info(message: Message, config: Config) -> None:
    await message.answer(
        f"Telegram-канал: {config.channel_url}\n"
        f"Поддержка: @{config.support_username}"
    )

