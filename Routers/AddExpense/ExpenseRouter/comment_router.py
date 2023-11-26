from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message, CallbackQuery

from Database.create_database import Expense as ExpenseDB
from Keyboards.Expense.delete import create_delete_expense_kb, DeleteExpense, ConfirmDeleteExpense
from Routers.AddExpense.expense_state_class import Expense
from create_bot import bot

commentRouter = Router()


@commentRouter.message(Expense.comment)
async def set_comment(message: Message, state: FSMContext):
    await message.delete()
    chat_id = message.chat.id
    comment = message.text
    data = (await state.get_data())

    date = data["date"]
    category_id = data["category"]["category_id"]
    category_name = data["category"]["category_name"]
    type_id = data["type"]["type_id"]
    type_name = data["type"]["type_name"]
    amount = data["amount"]

    expense = ExpenseDB.add_expense(date, category_id, type_id, amount, comment)
    expense_id = expense.id

    messages_ids = [data["date_message_id"], data["category_message_id"],
                    data["amount_message_id"], data["comment_message_id"]]

    await state.clear()

    try:
        for message_id in messages_ids:
            await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
    except:
        pass

    await message.answer(text=f"<b>✨ Добавлен расход</b>\n"
                              f"Дата: <code>{date}</code>\n"
                              f"Тип: <code>{type_name}</code>\n"
                              f"Категория: <code>{category_name}</code>\n"
                              f"Сумма: <code>{amount}</code>\n"
                              f"Комментарий: <code>{comment}</code>\n",
                         reply_markup=create_delete_expense_kb(expense_id=expense_id, confirm=False))


@commentRouter.callback_query(DeleteExpense.filter(F.delete == True))
async def confirm_delete_expense(query: CallbackQuery, callback_data: DeleteExpense):
    await query.answer()
    expense_id = callback_data.expense_id
    await query.message.edit_reply_markup(reply_markup=create_delete_expense_kb(expense_id, True))


@commentRouter.callback_query(ConfirmDeleteExpense.filter(F.confirm_delete == True))
async def delete_expense(query: CallbackQuery, callback_data: DeleteExpense):
    await query.answer()

    message_text = query.message.text
    expense_id = callback_data.expense_id

    try:
        ExpenseDB.delete_expense(expense_id)
        await query.message.edit_text(text="<b>***Удалено***</b>\n" + message_text, reply_markup=None)
    except ExpenseDB.DoesNotExist:
        await query.message.answer(text="Расход не найден")
    except:
        await query.message.answer(text=f"Неизвестная ошибка")


@commentRouter.callback_query(ConfirmDeleteExpense.filter(F.confirm_delete == False))
async def cancel_delete_expense(query: CallbackQuery, callback_data: ConfirmDeleteExpense):
    await query.answer()

    expense_id = callback_data.expense_id
    await query.message.edit_reply_markup(reply_markup=create_delete_expense_kb(expense_id=expense_id, confirm=False))
