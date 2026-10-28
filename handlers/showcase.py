from decimal import Decimal

from aiogram import F, Router
from aiogram.types import Message

from config import Config
from keyboards.inline import payment_keyboard
from keyboards.reply import SHOWCASE_BUTTON


router = Router(name="showcase")


def format_price(price: Decimal) -> str:
    if price % 1:
        return format(price, "f").rstrip("0").rstrip(".")
    return str(int(price))


@router.message(F.text == SHOWCASE_BUTTON)
async def show_product(message: Message, config: Config) -> None:
    # собираем описание товара из настроек
    text = (
        f"Название товара: {config.product_name}\n"
        f"Цена: {format_price(config.product_price)} ₽\n\n"
    )

    # кнопку оплаты показываем только для доступного товара
    if config.product_available:
        await message.answer(
            text + "Товар в наличии",
            reply_markup=payment_keyboard(config.seller_username),
        )
        return

    await message.answer(text + "Товар продан, в ближайшее время пополнение")

