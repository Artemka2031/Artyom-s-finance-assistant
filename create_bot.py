from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from commands import BotCommands
from config import settings

bot = Bot(token=str(settings.get("token")), parse_mode=ParseMode.HTML)


def set_commands(commands: BotCommands):
    for params in commands:
        print(params)
