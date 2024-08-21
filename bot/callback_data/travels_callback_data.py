from aiogram.filters.callback_data import CallbackData


class Travel(CallbackData, prefix="travel"):
    travel_id: str
