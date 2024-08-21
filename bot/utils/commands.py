from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Начало работы"),
        BotCommand(command="profile", description="Перейти в профиль"),
        BotCommand(command="menu", description="Перейти в главное меню"),
        BotCommand(command="travels", description="Перейти к путешествиям"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
