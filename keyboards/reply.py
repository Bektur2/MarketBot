from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


SHOWCASE_BUTTON = "Витрина"
PROFILE_BUTTON = "Личный профиль"
INFO_BUTTON = "Вся информация"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    # постоянное меню остаётся возле поля ввода
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SHOWCASE_BUTTON)],
            [KeyboardButton(text=PROFILE_BUTTON)],
            [KeyboardButton(text=INFO_BUTTON)],
            [KeyboardButton(text="Войти в админку")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выберите раздел",
    )



def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Добавить товар"), KeyboardButton(text="Добавить админа")],
        [KeyboardButton(text="Удалить товар")],
        [KeyboardButton(text="В главное меню")],
    ], resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True)
