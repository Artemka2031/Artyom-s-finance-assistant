from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from Routers.AddExpense.ExpenseRouter.amount_router import amountRouter
from Routers.AddExpense.ExpenseRouter.category_router import categoryRouter
from Routers.AddExpense.ExpenseRouter.comment_router import commentRouter
from Routers.AddExpense.expense_state_class import Expense
from Routers.AddExpense.ExpenseRouter.date_router import dateRouter

from Keyboards.Expense.category import create_today_kb

expensesRouter = Router()


@expensesRouter.message(Command("expense"))
@expensesRouter.message(F.text.casefold() == "расход")
async def start_expense_adding(message: Message, state: FSMContext) -> None:
    sent_message = await message.answer(text="Выберете дату расхода:",
                                        reply_markup=create_today_kb())
    await state.update_data(date_message_id=sent_message.message_id)
    await state.set_state(Expense.date)


@expensesRouter.message(Command("cancel_expense"))
@expensesRouter.message(F.text.casefold() == "отмена расхода")
async def delete_expense_adding(message: Message, state: FSMContext) -> None:
    await message.answer(text="Добавление расхода отменено")
    await state.clear()


# Добавляем роутер по рабе с датой
expensesRouter.include_router(dateRouter)

# Добавляем роутер для работы с категориями
expensesRouter.include_router(categoryRouter)

# Добавляем роутер для работы с суммой расхода
expensesRouter.include_router(amountRouter)

# Добавляем роутер для работы с суммой расхода
expensesRouter.include_router(commentRouter)
