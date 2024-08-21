from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.callback_data.accept_callback_data import Accept
from bot.callback_data.profile_callback_data import ProfileMenu, ProfileEdit
from bot.database import db
from bot.keyboards.inline_keyboards.accept_inline_keyboard import (
    get_accept_inline_keyboard,
)
from bot.keyboards.inline_keyboards.profile_inline_keyboard import (
    get_profile_edit_inline,
    get_profile_inline_keyboard,
)
from bot.keyboards.reply_keyboards.main_menu_reply_keyboard import (
    get_main_menu_reply_keyboard,
)
from bot.states.states_profile import StepsProfile
from bot.texts.menu_texts import menu_texts
from bot.texts.profile_texts import profile_texts
from bot.texts.registration_texts import registration_texts
from bot.utils.get_locations import get_locations


async def get_profile_menu(
    call: CallbackQuery,
    bot: Bot,
    callback_data: ProfileMenu,
    state: FSMContext,
) -> None:
    await call.message.delete()
    if callback_data.function == "edit":
        profile = await db.get_user_by_telegram_id(call.from_user.id)
        await call.message.answer(
            text=profile_texts["edit_profile"].format(
                name=call.from_user.first_name,
                age=profile["age"],
                location=profile["city"],
                bio=profile["bio"],
            ),
            reply_markup=get_profile_edit_inline(),
        )
        await state.set_state(StepsProfile.EDIT_PROFILE)
    elif callback_data.function == "back":
        await call.message.answer(
            text=menu_texts["menu"],
            reply_markup=get_main_menu_reply_keyboard(),
        )
        await state.clear()
    await call.answer()


async def edit_profile(
    call: CallbackQuery,
    bot: Bot,
    callback_data: ProfileEdit,
    state: FSMContext,
) -> None:
    await call.message.delete()
    if callback_data.function == "edit_age":
        await call.message.answer(text=registration_texts["age_question"])
        await state.set_state(StepsProfile.EDIT_AGE)
    elif callback_data.function == "edit_city":
        await call.message.answer(text=registration_texts["location_question"])
        await state.set_state(StepsProfile.EDIT_CITY)
    elif callback_data.function == "edit_bio":
        await call.message.answer(text=registration_texts["bio_question"])
        await state.set_state(StepsProfile.EDIT_BIO)
    elif callback_data.function == "back":
        profile = await db.get_user_by_telegram_id(call.from_user.id)
        await call.message.answer(
            text=profile_texts["profile"].format(
                name=call.from_user.first_name,
                age=profile["age"],
                location=profile["city"],
                bio=profile["bio"],
            ),
            reply_markup=get_profile_inline_keyboard(),
        )
        await state.set_state(StepsProfile.GET_PROFILE)
    await call.answer()


async def edit_age(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await db.update_users_age_by_telegram_id(
            telegram_id=message.from_user.id,
            age=message.text,
        )
        await message.answer(
            f"Возраст успешно изменён🎉",
        )

        profile = await db.get_user_by_telegram_id(message.from_user.id)
        await message.answer(
            text=profile_texts["profile"].format(
                name=message.from_user.first_name,
                age=profile["age"],
                location=profile["city"],
                bio=profile["bio"],
            ),
            reply_markup=get_profile_edit_inline(),
        )
        await state.set_state(StepsProfile.EDIT_PROFILE)
    else:
        await message.answer(text=registration_texts["age_error"])


async def edit_city(message: Message, state: FSMContext) -> None:
    city = get_locations(message.text)["address"]
    if city:
        await message.answer(
            f"Вы находитесь в {city}❓",
            reply_markup=get_accept_inline_keyboard(),
        )
        await state.update_data(city=city)
        await state.set_state(StepsProfile.EDIT_CITY_ACCEPT)
    else:
        await message.answer(registration_texts["age_error"])


async def select_edit_city(
    call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    contex_data = await state.get_data()
    city = contex_data.get("city", "unknown")
    if callback_data.accept:
        await db.update_users_city_by_telegram_id(
            telegram_id=call.from_user.id,
            city=city,
        )
        await call.message.edit_text(
            f"Вы успешно сменили местоположение на {city}🎉",
        )

        profile = await db.get_user_by_telegram_id(call.from_user.id)
        await call.message.answer(
            text=profile_texts["edit_profile"].format(
                name=call.from_user.first_name,
                age=profile["age"],
                location=profile["city"],
                bio=profile["bio"],
            ),
            reply_markup=get_profile_edit_inline(),
        )
        await state.set_state(StepsProfile.EDIT_PROFILE)
    else:
        await call.message.edit_text(f"❌Вы не выбрали город {city}")
        await call.message.answer(registration_texts["location_question"])
        await state.set_state(StepsProfile.EDIT_CITY)
    await call.answer()


async def edit_bio(message: Message, state: FSMContext) -> None:
    await db.update_users_bio_by_telegram_id(
        telegram_id=message.from_user.id,
        bio=message.text,
    )
    await message.answer(
        f"Информация о себе успешно изменена!🎉",
    )

    profile = await db.get_user_by_telegram_id(message.from_user.id)
    await message.answer(
        text=profile_texts["edit_profile"].format(
            name=message.from_user.first_name,
            age=profile["age"],
            location=profile["city"],
            bio=profile["bio"],
        ),
        reply_markup=get_profile_edit_inline(),
    )
    await state.set_state(StepsProfile.EDIT_PROFILE)
