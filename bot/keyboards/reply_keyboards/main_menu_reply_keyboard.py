from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.handlers.main_menu.main_menu_buttons_texts import main_menu_buttons_texts


def get_main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()

    for button_text in main_menu_buttons_texts.values():
        keyboard_builder.button(text=button_text)
    keyboard_builder.adjust(2, 1)
    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите действие!",
    )
