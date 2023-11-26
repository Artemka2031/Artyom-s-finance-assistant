from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message

from Keyboards.Expense.category import create_today_kb
from Routers.AddExpense.ExpenseRouter.amount_router import amountRouter
from Routers.AddExpense.ExpenseRouter.category_router import categoryRouter
from Routers.AddExpense.ExpenseRouter.comment_router import commentRouter
from Routers.AddExpense.ExpenseRouter.date_router import dateRouter
from Routers.AddExpense.expense_state_class import Expense
from create_bot import bot

expensesRouter = Router()


@expensesRouter.message(Command("expense"))
@expensesRouter.message(F.text.casefold() == "расход")
async def start_expense_adding(message: Message, state: FSMContext) -> None:
    await state.clear()
    sent_message = await message.answer(text="Выберете дату расхода:",
                                        reply_markup=create_today_kb())
    await state.update_data(date_message_id=sent_message.message_id)
    await state.set_state(Expense.date)


@expensesRouter.message(Command("cancel_expense"))
@expensesRouter.message(F.text.casefold() == "отмена расхода")
async def delete_expense_adding(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id
    data = await state.get_data()
    await message.delete()

    fields_to_check = ["date_message_id", "category_message_id", "amount_message_id", "comment_message_id"]

    delete_messages = [data[field] for field in fields_to_check if field in data]

    extra_messages = data.get("extra_messages", [])
    delete_messages.extend(extra_messages)

    for message_id in delete_messages:
        await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))

    await message.answer(text="Расход отменён")
    await state.clear()


# Добавляем роутер по работе с датой
expensesRouter.include_router(dateRouter)

# Добавляем роутер для работы с категориями
expensesRouter.include_router(categoryRouter)

# Добавляем роутер для работы с суммой расхода
expensesRouter.include_router(amountRouter)

# Добавляем роутер для работы с суммой расхода
expensesRouter.include_router(commentRouter)
