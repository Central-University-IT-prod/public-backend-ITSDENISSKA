from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data.travels_callback_data import Travel
from bot.callback_data.travels_points_callback_data import (
    TravelPoint,
    TravelPointsMenuFunction,
    TravelMenuFunction,
)


def get_all_travels_inline_keyboard(travels: list) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    for travel in travels:
        keyboard_builder.button(
            text=f"\"{travel["travel_name"]}\" #{travel["travel_id"]}",
            callback_data=Travel(
                travel_id=travel["travel_id"],
            ),
        )

    keyboard_builder.adjust(1)

    functions_keyboard_builder = InlineKeyboardBuilder()

    functions_keyboard_builder.button(
        text="⬅️",
        callback_data=TravelMenuFunction(
            function="back",
        ),
    )
    functions_keyboard_builder.button(
        text="➕",
        callback_data=TravelMenuFunction(
            function="add",
        ),
    )

    keyboard_builder.attach(functions_keyboard_builder)

    return keyboard_builder.as_markup()


def get_travel_points_inline_keyboard(
        travel_id: str, travel_points: list[dict]
) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    travel_points.sort(key=lambda x: x.get("start_date", "unknown"))

    for travel_point in travel_points:
        keyboard_builder.button(
            text=f"{travel_point.get("travel_point_name", "unknown")} {travel_point.get("start_date", "unknown")} - {travel_point.get("end_date", "unknown")}",
            callback_data=TravelPoint(
                travel_point_id=str(travel_point.get("_id", "unknown")),
            )
        )

    keyboard_builder.adjust(1)

    functions_keyboard_builder = InlineKeyboardBuilder()

    functions_keyboard_builder.button(
        text="🗺️Маршрут",
        callback_data=TravelPointsMenuFunction(
            travel_id=travel_id,
            function="route",
        ),
    )

    functions_keyboard_builder.button(
        text="📝Заметки",
        callback_data=TravelPointsMenuFunction(
            travel_id=travel_id,
            function="notes",
        ),
    )

    functions_keyboard_builder.button(
        text="⬅️",
        callback_data=TravelPointsMenuFunction(
            travel_id=travel_id,
            function="back",
        ),
    )

    functions_keyboard_builder.button(
        text="➕",
        callback_data=TravelPointsMenuFunction(
            travel_id=travel_id,
            function="add",
        ),
    )

    functions_keyboard_builder.button(
        text="❌",
        callback_data=TravelPointsMenuFunction(
            travel_id=travel_id,
            function="remove",
        ),
    )
    functions_keyboard_builder.adjust(1, 1, 3)

    keyboard_builder.attach(functions_keyboard_builder)
    return keyboard_builder.as_markup()
