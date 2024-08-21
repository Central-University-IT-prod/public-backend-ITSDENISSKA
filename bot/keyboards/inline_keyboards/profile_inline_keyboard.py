from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data.profile_callback_data import ProfileMenu, ProfileEdit


def get_profile_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="⬅️",
        callback_data=ProfileMenu(
            function="back",
        ),
    )
    keyboard_builder.button(
        text="✏️",
        callback_data=ProfileMenu(
            function="edit",
        ),
    )

    return keyboard_builder.as_markup()


def get_profile_edit_inline() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="🎂Изменить возраст", callback_data=ProfileEdit(function="edit_age")
    )

    keyboard_builder.button(
        text="🏡Изменить город", callback_data=ProfileEdit(function="edit_city")
    )

    keyboard_builder.button(
        text="ℹ️Изменить информацию о себе",
        callback_data=ProfileEdit(function="edit_bio"),
    )

    keyboard_builder.button(text="⬅️", callback_data=ProfileEdit(function="back"))

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
