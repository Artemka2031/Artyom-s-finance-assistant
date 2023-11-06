import logging
from datetime import datetime
import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Keyboards.Expense.category import create_category_button, add_expense_kb, DateChooseCallback

expensesRouter = Router()


class Expense(StatesGroup):
    query_message = State()
    date = State()
    set_date = State()
    get_date = State()
    category = State()
    type = State()
    amount = State()
    comment = State()


@expensesRouter.message(Command("expense"))
@expensesRouter.message(F.text.casefold() == "расход")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.set_state(Expense.current_date)

    today = datetime.today()
    formatted_date = today.strftime('%d.%m.%y')

    await state.update_data(date=formatted_date)

    await message.answer(text="Добавьте параметры расхода",
                         reply_markup=add_expense_kb(formatted_date))


@expensesRouter.callback_query(DateChooseCallback.filter())
async def change_date(query: CallbackQuery, state: FSMContext):
    await query.answer()

    await query.message.answer(text='Напишите дату в формате "дд.мм.гг":')
    await state.set_state(Expense.get_date)


@expensesRouter.message(Expense.get_date, re.match(r'\d{2}.\d{2}.\d{2}', F.text) is None)
async def invalid_date_format(message: Message, state: FSMContext):
    await message.answer(text="Введённая дата не того формата, повторите:")
    await state.set_state(Expense.get_date)


@expensesRouter.message(Expense.get_date)
async def get_date(message: Message, state: FSMContext):
    date = message.text
    await state.update_data(date=date)