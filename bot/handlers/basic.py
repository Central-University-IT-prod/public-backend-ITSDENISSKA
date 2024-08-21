from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.database.database import db
from bot.keyboards.reply_keyboards.main_menu_reply_keyboard import (
    get_main_menu_reply_keyboard,
)
from bot.states.states_registration import StepsRegistration
from bot.texts.menu_texts import menu_texts


async def get_start(message: Message, bot: Bot, state: FSMContext) -> None:
    user = await db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            text=f"✨Привет {message.from_user.first_name}, Добро пожаловать в ПутеБот!✨",
        )
        await message.answer(
            text=f"🤗Давай познакомимся, Сколько тебе лет?",
        )
        await state.set_state(StepsRegistration.GET_AGE)
    else:
        await message.answer(
            text=menu_texts["menu"],
            reply_markup=get_main_menu_reply_keyboard(),
        )
        await state.clear()


async def not_select_accept(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Нажми на кнопку выше❗",
    )
