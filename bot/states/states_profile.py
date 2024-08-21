from aiogram.fsm.state import StatesGroup, State


class StepsProfile(StatesGroup):
    GET_PROFILE = State()
    EDIT_PROFILE = State()
    EDIT_AGE = State()
    EDIT_CITY = State()
    EDIT_CITY_ACCEPT = State()
    EDIT_BIO = State()
