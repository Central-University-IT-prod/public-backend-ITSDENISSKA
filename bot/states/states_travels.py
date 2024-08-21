from aiogram.fsm.state import StatesGroup, State


class StepsTravels(StatesGroup):
    GET_TRAVELS = State()
    GET_TRAVEL_NAME = State()
    GET_TRAVEL = State()
    GET_REMOVE_TRAVEL_ACCEPT = State()
    GET_REMOVE_TRAVEL_POINT_ACCEPT = State()
    GET_TRAVEL_POINT = State()
    GET_TRAVEL_POINT_NAME = State()
    GET_TRAVEL_POINT_ACCEPT = State()
    GET_TRAVEL_POINT_START_DATE = State()
    GET_TRAVEL_POINT_END_DATE = State()
    EDIT_TRAVEL_POINT = State()
    EDIT_TRAVEL_POINT_NAME = State()
    EDIT_TRAVEL_POINT_ACCEPT = State()
    EDIT_TRAVEL_POINT_START_DATE = State()
    EDIT_TRAVEL_POINT_END_DATE = State()
    GET_NOTES = State()
    ADD_NOTES = State()
    GET_PHOTO_NOTE = State()
    GET_FILE_NOTE = State()
