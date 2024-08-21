from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data.travels_points_callback_data import (
    TravelPointFunction,
    TravelPointEdit,
    NoteFunction,
    EditNoteFunction,
    TravelPointsMenu,
)


def get_notes_inline_keyboard(travel_id: str) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="🖼️Фото-заметки",
        callback_data=NoteFunction(
            travel_id=travel_id,
            function="images",
        ),
    )

    keyboard_builder.button(
        text="📋Документы-заметки",
        callback_data=NoteFunction(
            travel_id=travel_id,
            function="files",
        ),
    )

    keyboard_builder.button(
        text="⬅️",
        callback_data=NoteFunction(
            travel_id=travel_id,
            function="back",
        ),
    )
    keyboard_builder.adjust(1, 1, 1)
    return keyboard_builder.as_markup()


def get_note_edit_inline_keyboard(
    travel_id: str, edit_function: str
) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="⬅️",
        callback_data=EditNoteFunction(
            travel_id=travel_id,
            function="back",
        ),
    )

    keyboard_builder.button(
        text="➕",
        callback_data=EditNoteFunction(
            travel_id=travel_id,
            function=edit_function,
        ),
    )

    return keyboard_builder.as_markup()


def get_travel_point_inline_keyboard(travel_point_id: str) -> InlineKeyboardMarkup:
    function_keyboard_builder = InlineKeyboardBuilder()

    function_keyboard_builder.button(
        text="🧋Кафе рядом",
        callback_data=TravelPointsMenu(
            travel_point_id=travel_point_id, function="cafe"
        ),
    )

    function_keyboard_builder.button(
        text="🗽Достопремечательности рядом",
        callback_data=TravelPointsMenu(
            travel_point_id=travel_point_id, function="attraction"
        ),
    )

    function_keyboard_builder.button(
        text="🛏️Отели рядом",
        callback_data=TravelPointsMenu(
            travel_point_id=travel_point_id, function="hotel"
        ),
    )

    function_keyboard_builder.button(
        text="🎫Билеты сюда",
        callback_data=TravelPointsMenu(
            travel_point_id=travel_point_id, function="tickets"
        ),
    )

    function_keyboard_builder.button(
        text="🌧Погода здесь",
        callback_data=TravelPointsMenu(
            travel_point_id=travel_point_id, function="weather"
        ),
    )

    function_keyboard_builder.adjust(1)

    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="⬅️",
        callback_data=TravelPointFunction(
            travel_point_id=travel_point_id,
            function="back",
        ),
    )
    keyboard_builder.button(
        text="✏️",
        callback_data=TravelPointFunction(
            travel_point_id=travel_point_id,
            function="edit",
        ),
    )
    keyboard_builder.button(
        text="❌",
        callback_data=TravelPointFunction(
            travel_point_id=travel_point_id,
            function="remove",
        ),
    )
    function_keyboard_builder.attach(keyboard_builder)
    return function_keyboard_builder.as_markup()


def get_travel_point_edit_inline(travel_point_id: str) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="🏙️Изменить место",
        callback_data=TravelPointEdit(
            travel_point_id=travel_point_id, function="edit_point_name"
        ),
    )

    keyboard_builder.button(
        text="📅Изменить дату начала посещения",
        callback_data=TravelPointEdit(
            travel_point_id=travel_point_id, function="edit_start_date"
        ),
    )

    keyboard_builder.button(
        text="📅Изменить дату конца посещения",
        callback_data=TravelPointEdit(
            travel_point_id=travel_point_id, function="edit_end_date"
        ),
    )

    keyboard_builder.button(
        text="⬅️",
        callback_data=TravelPointEdit(travel_point_id=travel_point_id, function="back"),
    )

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
