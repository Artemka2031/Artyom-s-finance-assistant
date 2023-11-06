from aiogram import Bot
from aiogram.enums import ParseMode

from config import settings

bot = Bot(token=str(settings.get("token")), parse_mode=ParseMode.HTML)