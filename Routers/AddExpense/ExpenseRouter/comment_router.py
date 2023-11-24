from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Routers.AddExpense.expense_state_class import Expense
from Database.create_database import Expense as ExpenseDB

commentRouter = Router()


@commentRouter.message(Expense.comment)
async def set_comment(message: Message, state: FSMContext):
    comment = message.text
    data = (await state.get_data())

    date = data["date"]
    category_id = data["category"]["category_id"]
    category_name = data["category"]["category_name"]
    type_id = data["type"]["type_id"]
    type_name = data["type"]["type_name"]
    amount = data["amount"]

    ExpenseDB.add_expense(date, category_id, type_id, amount, comment)

    await message.answer(text=f"<b>✨ Добавлен расход</b>\n"
                              f"Дата: <code>{date}</code>\n"
                              f"Тип: <code>{type_name}</code>\n"
                              f"Категория: <code>{category_name}</code>\n"
                              f"Сумма: <code>{amount}</code>\n"
                              f"Комментарий: <code>{comment}</code>\n")
