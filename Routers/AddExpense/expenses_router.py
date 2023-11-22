import time

from aiogram import Router, F
from aiogram.filters import Command, Filter
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Keyboards.Expense.category import TodayCallback, create_today_kb

expensesRouter = Router()


class CheckDate(Filter):
    def __init__(self, date: str) -> None:
        self.date = date

    async def __call__(self, message: Message) -> bool:
        self.date = message.text
        try:
            valid_date = time.strptime(self.date, '%m/%d/%Y')
            print(valid_date)
        except ValueError:
            return False

        return True


class Expense(StatesGroup):
    date = State()
    category = State()
    type = State()
    amount = State()
    comment = State()


@expensesRouter.message(Command("expense"))
@expensesRouter.message(F.text.casefold() == "расход")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await message.answer(text="Выберете дату расхода:",
                         reply_markup=create_today_kb())
    await state.set_state(Expense.date)


@expensesRouter.callback_query(Expense.date, TodayCallback.filter())
async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext):
    await state.set_state(Expense.date)
    date = callback_data.today
    await query.answer(f"Выбрана дата:{date}")

    await state.update_data(date=date)

    await state.set_state(Expense.category)


@expensesRouter.message(Expense.date, CheckDate(F.text))
async def invalid_date_format(message: Message, state: FSMContext):
    print("В хэндлере")
    await message.answer(text="Введённая дата не того формата, повторите:")
    await state.set_state(Expense.date)


@expensesRouter.message(Expense.date)
async def set_date_text(message: Message, state: FSMContext):
    date = message.text
    await state.update_data(date=date)

    await message.answer(text="Выберите категорию:")

    await state.set_state(Expense.category)
