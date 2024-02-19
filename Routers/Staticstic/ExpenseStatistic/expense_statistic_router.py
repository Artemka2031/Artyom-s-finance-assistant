from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Database.Tables.ExpensesTables import Expense

expenseStatisticRouter = Router()


@expenseStatisticRouter.message(Command("expense_statistic"))
async def start_messaging(message: Message) -> None:
    # expenses = Expense.get_by_time_interval()
    expenses = None
    await message.answer(f"{hbold('Расходы: ')}\n{expenses}")
