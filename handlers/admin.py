import re
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import admin_keyboard, cancel_keyboard, main_menu_keyboard

from config import Config
from database import Database

router = Router(name="admin")


def money(value: str) -> str:
    try:
        amount = Decimal(value.replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("Введите неотрицательную сумму") from error
    if not amount.is_finite() or amount < 0 or amount > 10**15:
        raise ValueError("Сумма должна быть от 0 до 1000000000000000")
    return str(amount)


def username(value: str) -> str:
    value = value.removeprefix("@")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", value):
        raise ValueError("Введите корректный Telegram username")
    return value


@router.message(Command("add_product", "delete_product", "set_name", "set_price",
                        "set_available", "set_payment_username", "set_balance",
                        "set_purchases", "products"))
async def manage(message: Message, command: CommandObject, config: Config, database: Database) -> None:
    if message.from_user is None or not await database.is_admin(message.from_user.id, message.from_user.username, config.admin_id):
        await message.answer("Команда доступна только администратору")
        return
    args = command.args or ""
    try:
        if command.command == "products":
            products = await database.get_products()
            if not products:
                await message.answer("Товаров пока нет")
            for product in products:
                await message.answer(f"ID: {product['id']} | {product['name']} | {product['price']} ₽ | "
                                     f"Наличие: {bool(product['available'])} | @{product['payment_username']}")
            return
        if command.command == "add_product":
            parts = [part.strip() for part in args.split("|")]
            if len(parts) != 2 or not parts[0]:
                raise ValueError("Формат: /add_product Название | 1500")
            if not message.from_user.username:
                raise ValueError("Укажите username в настройках Telegram для получения оплаты")
            if len(parts[0]) > 500:
                raise ValueError("Название должно быть не длиннее 500 символов")
            product_id = await database.add_product(parts[0], money(parts[1]), message.from_user.username)
            await message.answer(f"Товар добавлен. ID: {product_id}")
            return
        parts = args.split(maxsplit=1)
        expected = 1 if command.command == "delete_product" else 2
        if len(parts) != expected or not parts[0].isdigit() or not 0 < int(parts[0]) < 2**63:
            raise ValueError(f"Формат: /{command.command} ID" + (" значение" if expected == 2 else ""))
        item_id = int(parts[0])
        if command.command == "delete_product":
            changed = await database.delete_product(item_id)
        else:
            value = parts[1].strip()
            field = command.command.removeprefix("set_")
            if field in {"balance", "purchases"}:
                if not value.isdigit() or int(value) >= 2**63:
                    raise ValueError("Введите неотрицательное целое число меньше 9223372036854775808")
                changed = await database.set_user(item_id, "purchases_count" if field == "purchases" else field, int(value))
            else:
                if field == "price":
                    value = money(value)
                elif field == "available":
                    if value.lower() not in {"true", "false"}:
                        raise ValueError("Наличие: true или false")
                    value = int(value.lower() == "true")
                elif field == "payment_username":
                    value = username(value)
                elif not value or len(value) > 500:
                    raise ValueError("Название должно содержать от 1 до 500 символов")
                changed = await database.set_product(item_id, field, value)
        await message.answer("Готово" if changed else "Запись с таким ID не найдена")
    except ValueError as error:
        await message.answer(str(error))


class AdminForm(StatesGroup):
    name = State()
    price = State()
    admin = State()


@router.message(F.text.in_({"Войти в админку", "Добавить товар", "Добавить админа", "Удалить товар", "Отмена", "В главное меню"}))
async def admin_menu(message: Message, state: FSMContext, database: Database, config: Config) -> None:
    if message.from_user is None or not await database.is_admin(message.from_user.id, message.from_user.username, config.admin_id):
        await message.answer("Доступ только для администраторов")
        return
    await state.clear()
    if message.text == "В главное меню":
        await message.answer("Выберите раздел", reply_markup=main_menu_keyboard())
    elif message.text == "Добавить товар":
        if not message.from_user.username:
            await message.answer("Укажите username в настройках Telegram, чтобы покупатели могли написать вам для оплаты.", reply_markup=admin_keyboard())
            return
        await state.set_state(AdminForm.name)
        await message.answer("Введите название товара", reply_markup=cancel_keyboard())
    elif message.text == "Удалить товар":
        products = await database.get_products()
        if not products:
            await message.answer("Товаров пока нет", reply_markup=admin_keyboard())
        for product in products:
            await message.answer(
                f"{product['name']} — {product['price']} ₽",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="Удалить", callback_data=f"delete_product:{product['id']}")
                ]]),
            )
    elif message.text == "Добавить админа":
        await state.set_state(AdminForm.admin)
        await message.answer("Отправьте @username или Telegram ID нового администратора. Для добавления по @username он должен сначала нажать /start. По ID это не требуется.", reply_markup=cancel_keyboard())
    else:
        await message.answer("Админка", reply_markup=admin_keyboard())


@router.message(AdminForm.name)
@router.message(AdminForm.price)
@router.message(AdminForm.admin)
async def fill_admin_form(message: Message, state: FSMContext, database: Database, config: Config) -> None:
    if message.from_user is None or not await database.is_admin(message.from_user.id, message.from_user.username, config.admin_id):
        await state.clear()
        await message.answer("Доступ только для администраторов")
        return
    value = (message.text or "").strip()
    current = await state.get_state()
    try:
        if current == AdminForm.name.state:
            if not value or len(value) > 500 or value.startswith("/"):
                raise ValueError("Введите название от 1 до 500 символов")
            await state.update_data(name=value)
            await state.set_state(AdminForm.price)
            await message.answer("Введите цену в рублях, например 1500")
        elif current == AdminForm.price.state:
            price = money(value)
            if not message.from_user.username:
                raise ValueError("Укажите username в настройках Telegram и отправьте цену ещё раз.")
            data = await state.get_data()
            product_id = await database.add_product(data["name"], price, message.from_user.username)
            await state.clear()
            await message.answer(f"Товар добавлен в витрину и доступен для покупки. ID: {product_id}", reply_markup=admin_keyboard())
        else:
            if value.isascii() and value.isdigit():
                telegram_id = int(value)
                if not 0 < telegram_id < 2**63:
                    raise ValueError("Telegram ID должен быть положительным числом меньше 9223372036854775808")
            else:
                admin_username = username(value)
                user = await database.get_user_by_username(admin_username)
                if user is None:
                    raise ValueError("Пользователь не найден. Попросите его нажать /start или отправьте его Telegram ID.")
                telegram_id = user.telegram_id
            await database.add_admin(telegram_id)
            await state.clear()
            await message.answer("Администратор добавлен. Ему доступна кнопка «Войти в админку».", reply_markup=admin_keyboard())
    except ValueError as error:
        await message.answer(str(error))


@router.callback_query(F.data.startswith("delete_product:"))
@router.callback_query(F.data.startswith("confirm_delete:"))
@router.callback_query(F.data == "cancel_delete")
async def delete_product_button(callback: CallbackQuery, database: Database, config: Config) -> None:
    if not await database.is_admin(callback.from_user.id, callback.from_user.username, config.admin_id):
        await callback.answer("Доступ только для администраторов", show_alert=True)
        return
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    if callback.data == "cancel_delete":
        await callback.answer("Удаление отменено")
        await callback.message.edit_reply_markup(reply_markup=None)
        return
    action, raw_id = callback.data.split(":", 1)
    if not raw_id.isascii() or not raw_id.isdigit() or not 0 < int(raw_id) < 2**63:
        await callback.answer("Некорректный товар", show_alert=True)
        return
    product_id = int(raw_id)
    if action == "delete_product":
        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Да, удалить", callback_data=f"confirm_delete:{product_id}"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel_delete"),
        ]]))
    else:
        deleted = await database.delete_product(product_id)
        await callback.answer("Товар удалён" if deleted else "Товар уже удалён")
        await callback.message.edit_text("Товар удалён из витрины")
