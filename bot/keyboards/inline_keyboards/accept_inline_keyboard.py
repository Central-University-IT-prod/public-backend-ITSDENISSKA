from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data.accept_callback_data import Accept


def get_accept_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="✅", callback_data=Accept(accept=True))
    keyboard_builder.button(text="❌", callback_data=Accept(accept=False))

    return keyboard_builder.as_markup()
