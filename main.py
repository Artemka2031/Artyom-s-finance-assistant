import asyncio
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from Routers import startRouter, expensesRouter
from Routers.Edit import editExpenseCategoriesRouter

from create_bot import bot


async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(startRouter)
    dp.include_router(editExpenseCategoriesRouter)
    dp.include_router(expensesRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except :
        print('Закрываю бота')
