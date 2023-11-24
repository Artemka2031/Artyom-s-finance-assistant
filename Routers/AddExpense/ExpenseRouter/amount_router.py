from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Filters.check_amount import CheckAmount
from Routers.AddExpense.expense_state_class import Expense

amountRouter = Router()


@amountRouter.message(Expense.amount, CheckAmount(F.text))
async def incorrect_amount(message: Message, state: FSMContext):
    await message.answer("Введено недопустимое значение.")
    await state.set_state(Expense.amount)


@amountRouter.message(Expense.amount)
async def set_amount(message: Message, state: FSMContext):
    amount = float(message.text.replace(',', '.'))
    await state.update_data(amount=amount)

    await message.answer(text="Введите комментарий")

    await state.set_state(Expense.comment)
