from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.methods import EditMessageText
from aiogram.types import CallbackQuery, Message

from Filters.check_date import CheckDate
from Keyboards.Expense.category import TodayCallback, category_choose_kb
from Routers.AddExpense.expense_state_class import Expense
from create_bot import bot

dateRouter = Router()


@dateRouter.callback_query(Expense.date, TodayCallback.filter())
async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext):
    await state.set_state(Expense.date)
    date = callback_data.today
    await query.answer(f"Выбрана дата: {date}")
    await query.message.edit_text(f"Выбрана дата: {date}", reply_markup=None)

    await state.update_data(date=date)

    await query.message.answer(text="Выберите категорию:", reply_markup=category_choose_kb())
    await state.set_state(Expense.category)


@dateRouter.message(Expense.date, CheckDate(F.text))
async def invalid_date_format(message: Message, state: FSMContext):
    await message.answer(text="Дата должна быть от 2022 до 2030 и не позднее сегодняшнего дня. 📅 Повторите:")
    await state.set_state(Expense.date)


@dateRouter.message(Expense.date)
async def set_date_text(message: Message, state: FSMContext):
    date = message.text
    chat_id = message.chat.id

    await message.delete()

    await state.update_data(date=date)

    date_message_id = (await state.get_data())["date_message_id"]
    await bot(EditMessageText(chat_id=chat_id, message_id=date_message_id,
                              text=f"Выбрана дата: {date}", reply_markup=None))
    await message.answer(text="Выберите категорию:", reply_markup=category_choose_kb())

    await state.set_state(Expense.category)
