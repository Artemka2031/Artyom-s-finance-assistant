import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from Routers import startRouter, expensesRouter, editExpenseCategoriesRouter, expenseStatisticRouter
from create_bot import bot


async def main():
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(startRouter)
    dp.include_router(editExpenseCategoriesRouter)
    dp.include_router(expensesRouter)
    dp.include_router(expenseStatisticRouter)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("Бот запущен")
        asyncio.run(main())
    except:
        print('Закрываю бота')
