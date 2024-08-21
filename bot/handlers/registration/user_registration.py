from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.callback_data.accept_callback_data import Accept
from bot.database import db
from bot.keyboards.inline_keyboards.accept_inline_keyboard import get_accept_inline_keyboard
from bot.keyboards.reply_keyboards.main_menu_reply_keyboard import get_main_menu_reply_keyboard
from bot.states.states_registration import StepsRegistration
from bot.texts.registration_texts import registration_texts
from bot.utils.get_locations import get_locations


async def get_age(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await message.answer(
            text=registration_texts["location_question"],
        )
        await state.update_data(age=message.text)
        await state.set_state(StepsRegistration.GET_CITY)
    else:
        await message.answer(
            text=registration_texts["age_error"],
        )


async def choice_city(message: Message, state: FSMContext) -> None:
    city = get_locations(message.text)["address"]
    if city:
        await message.answer(
            text=f"Вы находитесь в {city}?",
            reply_markup=get_accept_inline_keyboard(),
        )
        await state.update_data(city=city)
        await state.set_state(StepsRegistration.GET_CITY_ACCEPT)
    else:
        await message.answer(text=registration_texts["city_error"])


async def select_city(
        call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    contex_data: dict = await state.get_data()
    if callback_data.accept:
        await call.message.edit_text(f"Вы выбрали город {contex_data.get("city", "unknown")}✨")
        await call.message.answer(text=registration_texts["bio_question"])
        await state.set_state(StepsRegistration.GET_BIO)
    else:
        await call.message.edit_text(f"Вы не выбрали город {contex_data.get("city", "unknown")}")
        await call.message.answer(text=registration_texts["location_question"])
        await state.set_state(StepsRegistration.GET_CITY)
    await call.answer()


async def get_bio(message: Message, state: FSMContext) -> None:
    await state.update_data(bio=message.text)
    contex_data: dict = await state.get_data()
    await message.answer(
        f"Пользователь зарегистрирован!🎉\r\nТы можешь изменить свои данные в профиле 👤",
        reply_markup=get_main_menu_reply_keyboard()
    )
    await db.create_user(
        telegram_id=message.from_user.id,
        age=contex_data.get("age", 0),
        city=contex_data.get("city", "unknown"),
        bio=contex_data.get("bio", "unknown"),
    )
    await state.clear()
