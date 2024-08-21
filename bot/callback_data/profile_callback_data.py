from aiogram.filters.callback_data import CallbackData


class ProfileMenu(CallbackData, prefix="profile_menu"):
    function: str


class ProfileEdit(CallbackData, prefix="profile_edit"):
    function: str
