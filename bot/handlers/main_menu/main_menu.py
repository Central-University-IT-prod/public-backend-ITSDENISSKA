from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database import db
from bot.keyboards.inline_keyboards.profile_inline_keyboard import (
    get_profile_inline_keyboard,
)
from bot.keyboards.inline_keyboards.travels_inline_keyboards import (
    get_all_travels_inline_keyboard,
)
from bot.states.states_profile import StepsProfile
from bot.states.states_travels import StepsTravels
from bot.texts.profile_texts import profile_texts


async def get_profile(message: Message, state: FSMContext) -> None:
    profile = await db.get_user_by_telegram_id(message.from_user.id)
    await message.answer(
        text=profile_texts["profile"].format(
            name=message.from_user.first_name,
            age=profile["age"],
            location=profile["city"],
            bio=profile["bio"],
        ),
        reply_markup=get_profile_inline_keyboard(),
    )
    await state.set_state(StepsProfile.GET_PROFILE)


async def get_travels(message: Message, state: FSMContext) -> None:
    travels = await db.get_travels_by_telegram_id(
        author_telegram_id=message.from_user.id
    )
    if travels:
        await message.answer(
            text=f"🌍Твои путешествия:",
            reply_markup=get_all_travels_inline_keyboard(travels),
        )
    else:
        await message.answer(
            text=f"Вы ещё не добавили путешествий 🌟",
            reply_markup=get_all_travels_inline_keyboard([]),
        )
    await state.set_state(StepsTravels.GET_TRAVELS)


async def add_travel_by_main_menu(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=f"📍Введите название нового путешествия",
    )
    await state.set_state(StepsTravels.GET_TRAVEL_NAME)
