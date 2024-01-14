from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from Database.db_base import Expense
from Database.time_intervals import TimeInterval

expenseStatisticRouter = Router()


@expenseStatisticRouter.message(Command("expense_statistic"))
async def start_messaging(message: Message) -> None:
    expenses = Expense.get_expenses_in_category_by_time_interval(TimeInterval.TODAY.value)
    await message.answer(f"{hbold('Расходы: ')}\n{expenses}")
