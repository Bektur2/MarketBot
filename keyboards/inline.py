from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_keyboard(seller_username: str) -> InlineKeyboardMarkup:
    # кнопка открывает личные сообщения продавца
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перейти к оплате",
                    url=f"https://t.me/{seller_username}",
                )
            ]
        ]
    )

