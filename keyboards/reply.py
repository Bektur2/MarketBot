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
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выберите раздел",
    )

