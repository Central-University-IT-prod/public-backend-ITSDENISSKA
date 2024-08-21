from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.callback_data.accept_callback_data import Accept
from bot.callback_data.travels_points_callback_data import TravelPointEdit, NoteFunction, \
    EditNoteFunction, TravelPointsMenu
from bot.database import db
from bot.keyboards.inline_keyboards.accept_inline_keyboard import get_accept_inline_keyboard
from bot.keyboards.inline_keyboards.travels_inline_keyboards import get_travel_points_inline_keyboard
from bot.keyboards.inline_keyboards.travels_points_inline_keyboards import get_notes_inline_keyboard, \
    get_note_edit_inline_keyboard, get_travel_point_inline_keyboard

from bot.states.states_travels import StepsTravels
from bot.texts.travel_texts import travel_texts
from bot.utils.get_attractions import get_attractions
from bot.utils.get_cafe import get_cafe
from bot.utils.get_hotels import get_hotels
from bot.utils.get_locations import get_locations
from bot.utils.get_tickets import get_tickets
from bot.utils.get_weather import get_weather
from bot.utils.media_group_builder import get_media_group_builders
from bot.utils.validate_date import validate_date


async def get_notes(
        call: CallbackQuery, bot: Bot, callback_data: NoteFunction, state: FSMContext
) -> None:
    travel = await db.get_travel_by_travel_id(travel_id=callback_data.travel_id)
    await call.message.delete()
    if callback_data.function == "back":
        travel_points = await db.get_travel_points_by_travel_id(travel_id=callback_data.travel_id)
        await call.message.answer(
            text=travel_texts["all_travels_menu"].format(travel_name=travel["travel_name"]),
            reply_markup=get_travel_points_inline_keyboard(
                travel_id=callback_data.travel_id,
                travel_points=travel_points,
            ),
        )
        await state.set_state(StepsTravels.GET_TRAVEL)
    elif callback_data.function == "images":
        notes = await db.get_notes_by_travel_id(travel_id=callback_data.travel_id)
        if notes.get("photos", None):
            media_group_builders = get_media_group_builders(
                media_elements=notes.get("photos", "unknown"),
                media_type="photo",
            )
            for media_group in media_group_builders:
                await call.message.answer_media_group(
                    media=media_group
                )
            await call.message.answer(
                text=f"Твои заметки-изображения ☝️☝️☝️",
                reply_markup=get_note_edit_inline_keyboard(
                    travel_id=callback_data.travel_id,
                    edit_function=callback_data.function,
                )
            )
        else:
            await call.message.answer(
                text=f"😔Ты ещё не добавил заметки-изображения",
                reply_markup=get_note_edit_inline_keyboard(
                    travel_id=callback_data.travel_id,
                    edit_function=callback_data.function,
                )
            )
        await state.set_state(StepsTravels.ADD_NOTES)
    elif callback_data.function == "files":
        notes = await db.get_notes_by_travel_id(travel_id=callback_data.travel_id)
        if notes.get("files", None):
            for file in notes.get("files", "unknown"):
                await call.message.answer_document(
                    document=file,
                )
            await call.message.answer(
                text=f"Твои заметки-файлы ☝️☝️☝️",
                reply_markup=get_note_edit_inline_keyboard(
                    travel_id=callback_data.travel_id,
                    edit_function=callback_data.function,
                )
            )
        else:
            await call.message.answer(
                text=f"😔Ты ещё не добавил заметки-файлы",
                reply_markup=get_note_edit_inline_keyboard(
                    travel_id=callback_data.travel_id,
                    edit_function=callback_data.function,
                )
            )
        await state.set_state(StepsTravels.ADD_NOTES)
    await call.answer()


async def add_note(
        call: CallbackQuery, bot: Bot, callback_data: EditNoteFunction, state: FSMContext
) -> None:
    context_data = await state.get_data()
    travel = await db.get_travel_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
    await call.message.delete()
    if callback_data.function == "back":
        await call.message.answer(
            text=f"📝Твои заметки:",
            reply_markup=get_notes_inline_keyboard(travel_id=callback_data.travel_id),
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_NOTES)
    elif callback_data.function == "images":
        await call.message.answer(
            text=f"🖼️Отправь мне <b>ОДНО</b> фото и я добавлю его в твои заметки",
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_PHOTO_NOTE)
    elif callback_data.function == "files":
        await call.message.answer(
            text=f"📋Отправь мне <b>ОДИН</b> файл и я добавлю его в твои заметки",
        )
        await state.update_data(travel_id=callback_data.travel_id)
        await state.set_state(StepsTravels.GET_FILE_NOTE)
    await call.answer()


async def get_photo_note(message: Message, bot: Bot, state: FSMContext) -> None:
    photo = message.photo[-1].file_id
    context_data = await state.get_data()
    await db.add_photo_to_travel_note(travel_id=context_data.get("travel_id", "unknown"), photo=photo)
    await message.answer(
        text=f"✅Добавил фото в замету",
    )

    notes = await db.get_notes_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
    media_group_builders = get_media_group_builders(
        media_elements=notes.get("photos", "unknown"),
        media_type="photo",
    )
    for media_group in media_group_builders:
        await message.answer_media_group(
            media=media_group
        )
    await message.answer(
        text=f"Твои заметки-изображения ☝️☝️☝️",
        reply_markup=get_note_edit_inline_keyboard(
            travel_id=context_data.get("travel_id", "unknown"),
            edit_function="images",
        )
    )
    await state.set_state(StepsTravels.ADD_NOTES)


async def get_file_note(message: Message, state: FSMContext) -> None:
    file = message.document.file_id
    context_data = await state.get_data()
    await db.add_file_to_travel_note(travel_id=context_data.get("travel_id", "unknown"), file=file)
    await message.answer(
        text=f"✅Добавил файл в замету",
    )

    notes = await db.get_notes_by_travel_id(travel_id=context_data.get("travel_id", "unknown"))
    for file in notes.get("files", "unknown"):
        await message.answer_document(
            document=file,
        )
    await message.answer(
        text=f"Твои заметки-файлы ☝️☝️☝️",
        reply_markup=get_note_edit_inline_keyboard(
            travel_id=context_data.get("travel_id", "unknown"),
            edit_function="images",
        )
    )
    await state.set_state(StepsTravels.ADD_NOTES)


async def choice_travel_point_edit(
        call: CallbackQuery, bot: Bot, callback_data: TravelPointEdit, state: FSMContext
) -> None:
    message = call.message
    await message.delete()
    await state.update_data(travel_point_id=callback_data.travel_point_id)
    if callback_data.function == "edit_point_name":
        await call.message.answer(
            text="🧭Какое место ты хочешь посетить?",
        )
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT_NAME)
    elif callback_data.function == "edit_start_date":
        await call.message.answer(
            text=f"📅Когда ты хочешь посетить это место?\r\n\n "
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)",
        )
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT_START_DATE)
    elif callback_data.function == "edit_end_date":
        await call.message.answer(
            text=f"📅Когда ты хочешь окончить посещения этого места?\r\n\n "
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)",
        )
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT_END_DATE)
    elif callback_data.function == "back":
        travel_point = await db.get_travel_point_by_travel_point_id(travel_point_id=callback_data.travel_point_id)
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
        await call.message.delete()
        await state.set_state(StepsTravels.GET_TRAVEL_POINT)
    await call.answer()


async def choice_travel_point_name_edit(message: Message, state: FSMContext) -> None:
    point_name = get_locations(message.text)["address"]
    if point_name:
        await message.answer(
            text=f"🗺️Ты хочешь посетить {point_name}?",
            reply_markup=get_accept_inline_keyboard(),
        )
        await state.update_data(point_name=point_name)
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT_ACCEPT)
    else:
        await message.answer(f"😔Не удалось найти такой город.\r\n\n"
                             f"❗Попробуй отправить название чуть конкретнее")


async def select_travel_point_name_edit(
        call: CallbackQuery, bot: Bot, callback_data: Accept, state: FSMContext
) -> None:
    context_data = await state.get_data()
    if callback_data.accept:
        await db.update_travel_point_name_by_travel_point_id(
            travel_point_id=context_data.get("travel_point_id", "unknown"),
            travel_point_name=context_data.get("point_name", "unknown"),
        )
        await call.message.edit_text(f"✅Ты изменил место на {context_data.get("point_name", "unknown")}")
        travel_point = await db.get_travel_point_by_travel_point_id(
            travel_point_id=context_data.get("travel_point_id", "unknown"),
        )
        message = call.message
        travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
        await message.answer(
            text=travel_texts["travel_menu"].format(
                travel_name=travel.get("travel_name", "unknown"),
                travel_place=travel_point.get("travel_point_name", "unknown"),
                start_date=travel_point.get("start_date", "unknown"),
                end_date=travel_point.get("end_date", "unknown"),
            ),
            reply_markup=get_travel_point_inline_keyboard(
                travel_point_id=context_data.get("travel_point_id", "unknown"))
        )
        await state.set_state(StepsTravels.GET_TRAVEL_POINT)
    else:
        await call.message.edit_text(f"❌Ты не изменил место на {context_data.get("point_name", "unknown")}")
        await call.message.answer(f"🧭Какое место ты хочешь посетить?")
        await state.set_state(StepsTravels.EDIT_TRAVEL_POINT_NAME)
    await call.answer()


async def edit_get_travel_point_start_date(message: Message, state: FSMContext) -> None:
    context_data = await state.get_data()
    travel_point = await db.get_travel_point_by_travel_point_id(
        travel_point_id=context_data.get("travel_point_id", "unknown"),
    )
    validate = validate_date(message.text, end_date=travel_point.get("end_date", "unknown"))
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
            await db.update_travel_point_start_date_by_travel_point_id(
                travel_point_id=context_data.get("travel_point_id", "unknown"),
                start_date=message.text,
            )
            await message.answer(
                text="✅Ты успешно изменили дату начала поездки",
            )
            travel_point = await db.get_travel_point_by_travel_point_id(
                travel_point_id=context_data.get("travel_point_id", "unknown"),
            )
            travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
            await message.answer(
                text=travel_texts["travel_menu"].format(
                    travel_name=travel.get("travel_name", "unknown"),
                    travel_place=travel_point.get("travel_point_name", "unknown"),
                    start_date=travel_point.get("start_date", "unknown"),
                    end_date=travel_point.get("end_date", "unknown"),
                ),
                reply_markup=get_travel_point_inline_keyboard(
                    travel_point_id=context_data.get("travel_point_id", "unknown"))
            )
            await state.set_state(StepsTravels.GET_TRAVEL_POINT)
    else:
        await message.answer(
            text="😉Ты ввёл дату в неверном формате\r\n\n"
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)",
        )


async def edit_get_travel_point_end_date(message: Message, state: FSMContext) -> None:
    context_data = await state.get_data()
    travel_point = await db.get_travel_point_by_travel_point_id(
        travel_point_id=context_data.get("travel_point_id", "unknown"),
    )
    validate = validate_date(message.text, start_date=travel_point.get("start_date", "unknown"))
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
            await db.update_travel_point_end_date_by_travel_point_id(
                travel_point_id=context_data.get("travel_point_id", "unknown"),
                end_date=message.text,
            )
            await message.answer(
                text="✅Ты успешно изменили дату конца поездки",
            )
            travel_point = await db.get_travel_point_by_travel_point_id(
                travel_point_id=context_data.get("travel_point_id", "unknown"),
            )
            travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
            await message.answer(
                text=travel_texts["travel_menu"].format(
                    travel_name=travel.get("travel_name", "unknown"),
                    travel_place=travel_point.get("travel_point_name", "unknown"),
                    start_date=travel_point.get("start_date", "unknown"),
                    end_date=travel_point.get("end_date", "unknown"),
                ),
                reply_markup=get_travel_point_inline_keyboard(
                    travel_point_id=context_data.get("travel_point_id", "unknown"))
            )
            await state.set_state(StepsTravels.GET_TRAVEL_POINT)
    else:
        await message.answer(
            text="😉Ты ввёл дату в неверном формате\r\n\n"
                 f"❗Введи дату в формате День.Месяц.Год (dd.mm.YYYY)"
        )


async def get_information_about_travel_point(
        call: CallbackQuery, bot: Bot, callback_data: TravelPointsMenu, state: FSMContext
) -> None:
    await call.message.delete()
    travel_point = await db.get_travel_point_by_travel_point_id(travel_point_id=callback_data.travel_point_id)
    if callback_data.function == "cafe":
        await call.message.answer(
            text=f"{get_cafe(
                lat=travel_point.get("latitude", "unknown"),
                lon=travel_point.get("longitude", "unknown"),
            )}",
        )
    elif callback_data.function == "attraction":
        await call.message.answer(
            text=f"{get_attractions(
                lat=travel_point.get("latitude", "unknown"),
                lon=travel_point.get("longitude", "unknown"),
            )}",
        )
    elif callback_data.function == "hotel":
        await call.message.answer(
            text=f"{get_hotels(
                lat=travel_point.get("latitude", "unknown"),
                lon=travel_point.get("longitude", "unknown"),
            )}",
        )
    elif callback_data.function == "tickets":
        profile = await db.get_user_by_telegram_id(telegram_id=call.from_user.id)
        tickets = get_tickets(
            origin=profile["city"],
            destination=travel_point.get("travel_point_name", "unknown"),
            date=travel_point.get("start_date", "unknown"),
        )
        if tickets["link"]:
            await call.message.answer(
                text=tickets["message"],
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🛫Купить на aviasales",
                                url=tickets["link"],
                            )
                        ]
                    ])
            )
        else:
            await call.message.answer(
                text=tickets["message"],
            )
    elif callback_data.function == "weather":
        await call.message.answer(
            text=f"{get_weather(
                lat=travel_point.get("latitude", "unknown"),
                lon=travel_point.get("longitude", "unknown"),
                date=travel_point.get("start_date", "unknown"),
            )}",
        )
    travel = await db.get_travel_by_travel_id(travel_id=travel_point.get("travel_id", "unknown"))
    await call.message.answer(
        text=travel_texts["travel_menu"].format(
            travel_name=travel.get("travel_name", "unknown"),
            travel_place=travel_point.get("travel_point_name", "unknown"),
            start_date=travel_point.get("start_date", "unknown"),
            end_date=travel_point.get("end_date", "unknown"),
        ),
        reply_markup=get_travel_point_inline_keyboard(
            travel_point_id=str(travel_point.get("_id", "unknown")))
    )
    await call.answer()
