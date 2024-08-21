from aiogram.fsm.state import StatesGroup, State


class StepsRegistration(StatesGroup):
    GET_AGE = State()
    GET_CITY = State()
    GET_CITY_ACCEPT = State()
    GET_BIO = State()
