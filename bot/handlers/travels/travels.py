import os

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.callback_data.accept_callback_data import Accept
from bot.callback_data.travels_callback_data import Travel
from bot.callback_data.travels_points_callback_data import TravelPoint, TravelPointFunction, TravelMenuFunction, \
    TravelPointsMenuFunction
from bot.database import db
from bot.keyboards.inline_keyboards.accept_inline_keyboard import get_accept_inline_keyboard
from bot.keyboards.inline_keyboards.travels_inline_keyboards import get_all_travels_inline_keyboard, \
    get_travel_points_inline_keyboard
from bot.keyboards.inline_keyboards.travels_points_inline_keyboards import get_travel_point_inline_keyboard, \
    get_travel_point_edit_inline, get_notes_inline_keyboard
from bot.keyboards.reply_keyboards.main_menu_reply_keyboard import get_main_menu_reply_keyboard

from bot.states.states_travels import StepsTravels
from bot.texts.menu_texts import menu_texts
from bot.texts.travel_texts import travel_texts
from bot.utils.get_locations import get_locations
from bot.utils.get_route import get_route
from bot.utils.validate_date import validate_date


async def add_travel(message: Message, state: FSMContext) -> None:
    travel = await db.create_travel(
        author_telegram_id=message.from_user.id,
        travel_name=message.text,
    )
    await message.answer(
        text=f"🎉Ты создал путшеcтвие \"{travel.get("travel_name", "unknown")}\" "
             f"#{travel.get("travel_id", "unknown")}\r\n\n"
             f"🗺️Ты можешь заполнить его во вкладке \"Мои путешествия\"",
        reply_markup=get_main_menu_reply_keyboard(),
    )

    await state.clear()


async def get_travel(
        call: CallbackQuery, bot: Bot, callback_data: Travel, state: FSMContext
) -> None:
    travel = await db.get_travel_by_travel_id(travel_id=callback_data.travel_id)
    message = call.message
    travel_points = await db.get_travel_points_by_travel_id(travel_id=callback_data.travel_id)
    await message.delete()
    await message.answer(
        text=travel_texts["all_travels_menu"].format(travel_name=travel.get("travel_name", "unknown")),
        reply_markup=get_travel_points_inline_keyboard(
            travel_id=callback_data.travel_id,
            travel_points=travel_points,
        ),
    )
    await call.answer()
    await state.set_state(StepsTravels.GET_TRAVEL)


async def remove_travel(
        call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    context_data = await state.get_data()
    travel = await db.get_travel_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
    if callback_data.accept:
        await db.delete_travel_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
        await call.message.edit_text(
            text=f"✅Ты удалил путешествие \"{travel.get("travel_name", "unknown")}\" "
                 f"#{context_data.get("travel_id", "unknown")}",
        )
    else:
        await call.message.edit_text(
            text=f"❌Ты отмении удаление путешествия \"{travel.get("travel_name", "unknown")}\" "
                 f"#{context_data.get("travel_id", "unknown")}",
        )
    travels = await db.get_travels_by_telegram_id(
        author_telegram_id=call.from_user.id
    )
    if travels:
        await call.message.answer(
            text=f"📍Твои путешествия:\r\n\n"
                 f"❗Для того чтобы узнать информацию о каком-либо путешествии, нажми на него",
            reply_markup=get_all_travels_inline_keyboard(travels),
        )
    else:
        await call.message.answer(
            text=f"😔Ты ещё не создал путешествия",
            reply_markup=get_all_travels_inline_keyboard([]),
        )
    await call.answer()
    await state.set_state(StepsTravels.GET_TRAVELS)


async def get_main_menu_by_travel_menu(
        call: CallbackQuery, bot: Bot, callback_data: TravelMenuFunction, state: FSMContext
) -> None:
    if callback_data.function == "back":
        await call.message.answer(
            text=menu_texts["menu"],
            reply_markup=get_main_menu_reply_keyboard(),
        )
        await call.message.delete()
        await state.clear()
    if callback_data.function == "add":
        await call.message.delete()
        await call.message.answer(
            text=f"📍Введи название твоего путешествия:",
        )
        await state.set_state(StepsTravels.GET_TRAVEL_NAME)
    await call.answer()


async def add_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: TravelPointsMenuFunction, state: FSMContext
) -> None:
    await call.message.delete()
    travel = await db.get_travel_by_travel_id(travel_id=callback_data.travel_id)
    if callback_data.function == "add":
        await call.message.answer(
            text="🧭Какое место ты хочешь посетить?",
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_TRAVEL_POINT_NAME)
    elif callback_data.function == "remove":
        await call.message.answer(
            text=f"Ты уверен что хочешь удалить путешествие \"{travel.get("travel_name", "unknown")}\" "
                 f"#{callback_data.travel_id}❓",
            reply_markup=get_accept_inline_keyboard()
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_REMOVE_TRAVEL_ACCEPT)
    elif callback_data.function == "back":
        travels = await db.get_travels_by_telegram_id(author_telegram_id=call.from_user.id)
        await call.message.answer(
            text=f"📍Твои путешествия:\r\n\n"
                 f"❗Для того чтобы узнать информацию о каком-либо путешествии, нажми на него",
            reply_markup=get_all_travels_inline_keyboard(travels),
        )
        await state.set_state(StepsTravels.GET_TRAVELS)
    elif callback_data.function == "notes":
        await call.message.answer(
            text=f"📝Твои заметки:",
            reply_markup=get_notes_inline_keyboard(travel_id=callback_data.travel_id),
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_NOTES)
    elif callback_data.function == "route":
        msg = await call.message.answer(
            text="🗺️Пожалуйста подожди, твой маршрут строится"
        )
        travel_points = await db.get_travel_points_by_travel_id(travel_id=callback_data.travel_id)
        travel_points.sort(key=lambda x: x.get("start_date", "unknown"))
        coords = [(travel_point["latitude"], travel_point["longitude"]) for travel_point in travel_points]
        photo_bytes = await get_route(coords)
        if photo_bytes:
            filename = f"{callback_data.travel_id}.png"
            with open(filename, "wb") as file:
                file.write(photo_bytes)
            await call.message.answer_photo(
                photo=FSInputFile(filename),
                caption=f"🗺Твой маршрут для путешествия \"{travel.get('travel_name', 'unknown')}\"",
            )
            os.remove(filename)
        else:
            await call.message.answer("😔Не удалось загрузить маршрутное изображение или "
                                      "в твоём маршруте менее двух точек")
        await msg.delete()
        await call.message.answer(
            text=travel_texts["all_travels_menu"].format(travel_name=travel.get("travel_name", "unknown")),
            reply_markup=get_travel_points_inline_keyboard(
                travel_id=callback_data.travel_id,
                travel_points=travel_points,
            ),
        )
    await call.answer()


async def choice_travel_point(message: Message, state: FSMContext) -> None:
    location = get_locations(message.text)
    point_name = location["address"]
    if point_name:
        await message.answer(
            f"🗺️Ты хочешь посетить {point_name}?",
            reply_markup=get_accept_inline_keyboard(),
        )
        await state.update_data(point_name=point_name)
        await state.update_data(latitude=location["latitude"])
        await state.update_data(longitude=location["longitude"])
        await state.set_state(StepsTravels.GET_TRAVEL_POINT_ACCEPT)
    else:
        await message.answer(f"😔Не удалось найти такой город.\r\n\n"
                             f"❗Попробуй отправить название чуть конкретнее")


async def select_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    context_data = await state.get_data()
    if callback_data.accept:
        await call.message.edit_text(f"✅Ты выбрал место {context_data.get("point_name", "unknown")}")
        await call.message.answer(f"📅Когда ты хочешь посетить это место?\r\n\n "
                                  f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)")
        await state.set_state(StepsTravels.GET_TRAVEL_POINT_START_DATE)
    else:
        await call.message.edit_text(
            text=f"❌Ты не выбрал место {context_data.get("point_name", "unknown")}",
        )
        await call.message.answer(
            text="🧭Какое место ты хочешь посетить?",
        )
        await state.set_state(StepsTravels.GET_TRAVEL_POINT_NAME)
    await call.answer()


async def get_travel_point_start_date(message: Message, state: FSMContext) -> None:
    validate = validate_date(message.text)
    if validate:
        if validate == "old_date_error":
            await message.answer(
                text="😇У тебя не получится отправиться в прошлое\r\n\n"
                     f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
            )
        else:
            await message.answer(
                text=f"📅Когда ты хочешь окончить посещения этого места?\r\n\n "
                     f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)",
            )

            await state.set_state(StepsTravels.GET_TRAVEL_POINT_END_DATE)
            await state.update_data(start_date=message.text)
    else:
        await message.answer(
            text="😉Ты ввёл дату в неверном формате\r\n\n"
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
        )


async def get_travel_point_end_date(message: Message, state: FSMContext) -> None:
    context_data = await state.get_data()
    validate = validate_date(message.text, start_date=context_data.get("start_date", "unknown"))
    if validate:
        if validate == "old_date_error":
            await message.answer(
                text="😇У тебя не получится отправиться в прошлое\r\n\n"
                     f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
            )
        elif validate == "timeline_error":
            await message.answer(
                text="😇Не балуйся со временем\r\n\n"
                     f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
            )
        else:
            await message.answer(
                text="✅Ты создал место для посещения в своём путешествии\r\n\n"
                     "❗Можешь отредактировать его"
            )
            await state.update_data(end_date=message.text)
            context_data = await state.get_data()
            travel_point = await db.add_travel_point_by_travel_id(
                travel_id=context_data.get("travel_id", "unknown"),
                travel_point_name=context_data.get("point_name", "unknown"),
                latitude=context_data.get("latitude", "unknown"),
                longitude=context_data.get("longitude", "unknown"),
                start_date=context_data.get("start_date", "unknown"),
                end_date=context_data.get("end_date", "unknown"),
            )
            travel = await db.get_travel_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
            travel_points = await db.get_travel_points_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
            await message.answer(
                text=travel_texts["all_travels_menu"].format(travel_name=travel.get("travel_name", "unknown")),
                reply_markup=get_travel_points_inline_keyboard(
                    travel_id=context_data.get("travel_id", "unknown"),
                    travel_points=travel_points,
                ),
            )
            await state.clear()
            await state.set_state(StepsTravels.GET_TRAVEL)
    else:
        await message.answer(
            text="😉Ты ввёл дату в неверном формате\r\n\n"
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
        )


async def get_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: TravelPoint, state: FSMContext
) -> None:
    travel_point = await db.get_travel_point_by_travel_point_id(travel_point_id=callback_data.travel_point_id)
    message = call.message
    await message.delete()
    travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    await message.answer(
        text=travel_texts["travel_menu"].format(
            travel_name=travel.get("travel_name", "unknown"),
            travel_place=travel_point.get("travel_point_name", "unknown"),
            start_date=travel_point.get("start_date", "unknown"),
            end_date=travel_point.get("end_date", "unknown"),
        ),
        reply_markup=get_travel_point_inline_keyboard(travel_point_id=callback_data.travel_point_id)
    )
    await call.answer()
    await state.set_state(StepsTravels.GET_TRAVEL_POINT)


async def edit_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: TravelPointFunction, state: FSMContext
) -> None:
    message = call.message
    await message.delete()
    travel_point = await db.get_travel_point_by_travel_point_id(travel_point_id=callback_data.travel_point_id)
    travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    travel_points = await db.get_travel_points_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    if callback_data.function == "back":
        await message.answer(
            text=travel_texts["all_travels_menu"].format(travel_name=travel.get("travel_name", "unknown")),
            reply_markup=get_travel_points_inline_keyboard(
                travel_id=travel.get("travel_id", "unknown"),
                travel_points=travel_points,
            ),
        )
        await state.set_state(StepsTravels.GET_TRAVEL)
    elif callback_data.function == "edit":
        await call.message.answer(
            text="🌆Выберете что вы хотите изменить",
            reply_markup=get_travel_point_edit_inline(travel_point_id=callback_data.travel_point_id)
        )
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT)
    elif callback_data.function == "remove":
        await call.message.answer(
            text=f"Вы уверены что хотите удалить точку \"{travel_point.get("travel_point_name", "unknown")}\"❓",
            reply_markup=get_accept_inline_keyboard()
        )
        await state.update_data(travel_point_id=callback_data.travel_point_id)
        await state.set_state(StepsTravels.GET_REMOVE_TRAVEL_POINT_ACCEPT)
    await call.answer()


async def remove_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    context_data = await state.get_data()
    travel_point = await db.get_travel_point_by_travel_point_id(
        travel_point_id=context_data.get("travel_point_id", "unknown"),
    )
    if callback_data.accept:
        await db.delete_travel_point(travel_point_id=context_data.get("travel_point_id", "unknown"))
        await call.message.edit_text(
            text=f"✅Вы удалили точку \"{travel_point.get("travel_point_name", "unknown")}\"",
        )
    else:
        await call.message.edit_text(
            text=f"❌Вы отменили удаление точки \"{travel_point.get("travel_point_name", "unknown")}\"",
        )
    travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    travel_points = await db.get_travel_points_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    await call.message.answer(
        text=travel_texts["all_travels_menu"].format(travel.get("travel_name", "unknown")),
        reply_markup=get_travel_points_inline_keyboard(
            travel_id=travel.get("travel_id", "unknown"),
            travel_points=travel_points,
        ),
    )
    await call.answer()
    await state.set_state(StepsTravels.GET_TRAVEL)
