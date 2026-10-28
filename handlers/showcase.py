from decimal import Decimal

from aiogram import F, Router
from aiogram.types import Message

from database import Database
from keyboards.inline import payment_keyboard
from keyboards.reply import SHOWCASE_BUTTON


router = Router(name="showcase")


def format_price(price: Decimal) -> str:
    if price % 1:
        return format(price, "f").rstrip("0").rstrip(".")
    return str(int(price))


@router.message(F.text == SHOWCASE_BUTTON)
async def show_product(message: Message, database: Database) -> None:
    products = await database.get_products()
    if not products:
        await message.answer("Товар продан, в ближайшее время пополнение")
    for product in products:
        # собираем описание товара из настроек
        text = (
            f"Название товара: {product['name']}\n"
            f"Цена: {format_price(Decimal(product['price']))} ₽\n\n"
        )
        # кнопку оплаты показываем только для доступного товара
        if product["available"]:
            await message.answer(
                text + "Товар в наличии",
                reply_markup=payment_keyboard(product["payment_username"]),
            )
        else:
            await message.answer(text + "Товар продан, в ближайшее время пополнение")
