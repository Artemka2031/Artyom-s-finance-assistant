from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText, DeleteMessage
from aiogram.types import Message

from Filters.check_amount import CheckAmount
from Routers.AddExpense.expense_state_class import Expense
from create_bot import bot

amountRouter = Router()


@amountRouter.message(Expense.amount, CheckAmount(F.text))
async def incorrect_amount(message: Message, state: FSMContext):
    await message.delete()

    try:
        extra_messages = (await state.get_data())["extra_messages"]
        if extra_messages is None:
            raise
    except:
        incorrect_amount_message = await message.answer(
            'Введено недопустимое значение. Должны быть только числа больше 0. Разделяющий знак = ","')
        incorrect_amount_message_id = incorrect_amount_message.message_id
        await state.update_data(extra_messages=[incorrect_amount_message_id])

    await state.set_state(Expense.amount)


@amountRouter.message(Expense.amount)
async def set_amount(message: Message, state: FSMContext):
    chat_id = message.chat.id

    try:
        extra_messages = (await state.get_data())["extra_messages"]

        for message_id in extra_messages:
            try:
                await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
            except:
                pass
    except:
        pass

    amount_message_id = (await state.get_data())["amount_message_id"]
    amount = float(message.text.replace(',', '.'))

    await state.update_data(amount=amount)
    await bot(EditMessageText(chat_id=chat_id, message_id=amount_message_id, text=f"Введённая сумма: {amount}"))
    await message.delete()

    comment_message = await message.answer(text="Введите комментарий")
    await state.update_data(comment_message_id=comment_message.message_id)

    await state.set_state(Expense.comment)
