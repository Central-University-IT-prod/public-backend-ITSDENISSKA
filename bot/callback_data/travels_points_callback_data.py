from aiogram.filters.callback_data import CallbackData


class TravelPointsMenu(CallbackData, prefix="travels_points_menu"):
    travel_point_id: str
    function: str


class TravelPoint(CallbackData, prefix="travels_points"):
    travel_point_id: str


class TravelPointsMenuFunction(CallbackData, prefix="travel_points_menu_function"):
    travel_id: str
    function: str


class TravelPointFunction(CallbackData, prefix="travel_point_function"):
    travel_point_id: str
    function: str


class TravelPointEdit(CallbackData, prefix="travel_point_edit"):
    travel_point_id: str
    function: str


class TravelMenuFunction(CallbackData, prefix="travel_menu_function"):
    function: str


class NoteFunction(CallbackData, prefix="note_function"):
    travel_id: str
    function: str


class EditNoteFunction(CallbackData, prefix="edit_not_function"):
    travel_id: str
    function: str
