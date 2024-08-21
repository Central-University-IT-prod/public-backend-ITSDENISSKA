import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from bot.callback_data.accept_callback_data import Accept
from bot.callback_data.profile_callback_data import ProfileMenu, ProfileEdit
from bot.callback_data.travels_callback_data import Travel
from bot.callback_data.travels_points_callback_data import (
    TravelPoint,
    TravelPointsMenuFunction,
    TravelPointFunction,
    TravelPointEdit,
    TravelMenuFunction,
    NoteFunction,
    EditNoteFunction,
    TravelPointsMenu,
)
from bot.handlers.main_menu.main_menu import (
    get_profile,
    get_travels,
    add_travel_by_main_menu,
)
from bot.handlers.main_menu.main_menu_buttons_texts import main_menu_buttons_texts
from bot.handlers.profile.profile import (
    get_profile_menu,
    edit_profile,
    edit_age,
    edit_city,
    edit_bio,
    select_edit_city,
)
from bot.handlers.travels.travels import (
    add_travel,
    get_travel,
    get_travel_point,
    choice_travel_point,
    select_travel_point,
    get_travel_point_start_date,
    get_travel_point_end_date,
    edit_travel_point,
    get_main_menu_by_travel_menu,
    remove_travel,
    remove_travel_point,
    add_travel_point,
)
from bot.handlers.travels_points.travels_points import (
    choice_travel_point_edit,
    choice_travel_point_name_edit,
    select_travel_point_name_edit,
    edit_get_travel_point_start_date,
    edit_get_travel_point_end_date,
    get_notes,
    add_note,
    get_photo_note,
    get_file_note,
    get_information_about_travel_point,
)
from bot.middlewares.apscheduler_middleware import SchedulerMiddleware
from bot.handlers.basic import (
    get_start,
    not_select_accept,
)
from bot.handlers.registration.user_registration import (
    get_age,
    get_bio,
    select_city,
    choice_city,
)
from bot.states.states_profile import StepsProfile
from bot.states.states_travels import StepsTravels
from bot.utils.commands import set_commands
from bot.states.states_registration import StepsRegistration
from bot.data.settings import settings


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - ($(filename)s).%(funcName)s(%(lineno)s) - %(message)s",
    )
    bot = Bot(
        token=settings.bots.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = RedisStorage.from_url(settings.bots.redis_url)

    dp = Dispatcher(storage=storage)

    jobstores = {
        "default": RedisJobStore(
            jobs_key="dispatched_trips_jobs",
            run_times_key="dispatched_trips_running",
            host=settings.bots.redis_host,
            db=2,
            port=6379,
        ),
    }

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores)
    )
    scheduler.ctx.add_instance(
        bot,
        declared_class=Bot,
    )
    scheduler.start()

    await set_commands(bot)

    dp.message.middleware.register(SchedulerMiddleware(scheduler))

    dp.message.register(
        get_start,
        Command(commands=["run", "start", "menu"]),
    )
    dp.message.register(
        get_profile,
        Command(commands=["profile"]),
    )
    dp.message.register(
        get_travels,
        Command(commands=["travels"]),
    )

    # Регистрация пользвателя в боте или изменение данных о нём
    dp.message.register(
        get_age,
        StepsRegistration.GET_AGE,
    )
    dp.message.register(
        choice_city,
        StepsRegistration.GET_CITY,
    )
    dp.callback_query.register(
        select_city,
        Accept.filter(),
        StepsRegistration.GET_CITY_ACCEPT,
    )
    dp.message.register(
        not_select_accept,
        StepsRegistration.GET_CITY_ACCEPT,
    )
    dp.message.register(
        get_bio,
        StepsRegistration.GET_BIO,
    )

    # Действия в главном меню
    dp.message.register(
        get_profile,
        F.text == main_menu_buttons_texts["profile"],
    )
    dp.message.register(
        get_travels,
        F.text == main_menu_buttons_texts["my_travels"],
    )
    dp.message.register(
        add_travel_by_main_menu,
        F.text == main_menu_buttons_texts["add_travel"],
    )

    # Действия в профиле
    dp.callback_query.register(
        get_profile_menu,
        ProfileMenu.filter(),
        StepsProfile.GET_PROFILE,
    )
    dp.callback_query.register(
        edit_profile,
        ProfileEdit.filter(),
        StepsProfile.EDIT_PROFILE,
    )
    dp.message.register(edit_age, StepsProfile.EDIT_AGE)
    dp.message.register(edit_bio, StepsProfile.EDIT_BIO)
    dp.message.register(edit_city, StepsProfile.EDIT_CITY)
    dp.callback_query.register(
        select_edit_city, Accept.filter(), StepsProfile.EDIT_CITY_ACCEPT
    )
    dp.message.register(not_select_accept, StepsProfile.EDIT_CITY_ACCEPT)
    # Действия с путешествиями
    dp.callback_query.register(
        get_main_menu_by_travel_menu,
        TravelMenuFunction.filter(),
        StepsTravels.GET_TRAVELS,
    )
    dp.message.register(
        add_travel,
        StepsTravels.GET_TRAVEL_NAME,
    )
    dp.callback_query.register(
        get_travel,
        Travel.filter(),
        StepsTravels.GET_TRAVELS,
    )
    dp.callback_query.register(
        get_travel_point,
        TravelPoint.filter(),
        StepsTravels.GET_TRAVEL,
    )
    dp.callback_query.register(
        add_travel_point,
        TravelPointsMenuFunction.filter(),
        StepsTravels.GET_TRAVEL,
    )
    dp.callback_query.register(
        remove_travel,
        Accept.filter(),
        StepsTravels.GET_REMOVE_TRAVEL_ACCEPT,
    )
    dp.message.register(not_select_accept, StepsTravels.GET_REMOVE_TRAVEL_ACCEPT)
    dp.callback_query.register(
        remove_travel_point,
        Accept.filter(),
        StepsTravels.GET_REMOVE_TRAVEL_POINT_ACCEPT,
    )
    dp.message.register(
        not_select_accept,
        StepsTravels.GET_REMOVE_TRAVEL_POINT_ACCEPT,
    )
    # Действия с точками путешествия
    dp.message.register(
        choice_travel_point,
        StepsTravels.GET_TRAVEL_POINT_NAME,
    )
    dp.callback_query.register(
        select_travel_point,
        Accept.filter(),
        StepsTravels.GET_TRAVEL_POINT_ACCEPT,
    )
    dp.message.register(
        not_select_accept,
        StepsTravels.GET_TRAVEL_POINT_ACCEPT,
    )
    dp.message.register(
        get_travel_point_start_date,
        StepsTravels.GET_TRAVEL_POINT_START_DATE,
    )
    dp.message.register(
        get_travel_point_end_date,
        StepsTravels.GET_TRAVEL_POINT_END_DATE,
    )
    dp.callback_query.register(
        edit_travel_point,
        TravelPointFunction.filter(),
        StepsTravels.GET_TRAVEL_POINT,
    )
    dp.callback_query.register(
        get_information_about_travel_point,
        TravelPointsMenu.filter(),
        StepsTravels.GET_TRAVEL_POINT,
    )
    dp.callback_query.register(
        choice_travel_point_edit,
        TravelPointEdit.filter(),
        StepsTravels.EDIT_TRAVEL_POINT,
    )
    dp.message.register(
        choice_travel_point_name_edit,
        StepsTravels.EDIT_TRAVEL_POINT_NAME,
    )
    dp.callback_query.register(
        select_travel_point_name_edit,
        Accept.filter(),
        StepsTravels.EDIT_TRAVEL_POINT_ACCEPT,
    )
    dp.message.register(
        not_select_accept,
        StepsTravels.EDIT_TRAVEL_POINT_ACCEPT,
    )
    dp.message.register(
        edit_get_travel_point_start_date,
        StepsTravels.EDIT_TRAVEL_POINT_START_DATE,
    )
    dp.message.register(
        edit_get_travel_point_end_date,
        StepsTravels.EDIT_TRAVEL_POINT_END_DATE,
    )
    # Работа с заметками
    dp.callback_query.register(
        get_notes,
        NoteFunction.filter(),
        StepsTravels.GET_NOTES,
    )
    dp.callback_query.register(
        add_note,
        EditNoteFunction.filter(),
        StepsTravels.ADD_NOTES,
    )
    dp.message.register(
        get_photo_note,
        F.photo,
        StepsTravels.GET_PHOTO_NOTE,
    )
    dp.message.register(
        get_file_note,
        F.document,
        StepsTravels.GET_FILE_NOTE,
    )

    # dp.message.register(get_info, Command(commands=["start"]))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
