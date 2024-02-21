import asyncio

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from Routers import startRouter, expensesRouter, editExpenseCategoriesRouter, expenseStatisticRouter, \
    editComingCategoriesRouter, comingsRouter
from commands import get_all_commands, bot_commands
from create_bot import bot


async def main():
    storage = MemoryStorage()

    await bot.set_my_commands(commands=get_all_commands())

    dp = Dispatcher(storage=storage)

    dp.include_router(startRouter)

    dp.include_router(editComingCategoriesRouter)
    dp.include_router(editExpenseCategoriesRouter)

    dp.include_router(expensesRouter)
    dp.include_router(comingsRouter)

    dp.include_router(expenseStatisticRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
