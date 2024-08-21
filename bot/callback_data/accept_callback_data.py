from aiogram.filters.callback_data import CallbackData


class Accept(CallbackData, prefix="accept"):
    accept: bool
