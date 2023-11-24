import time
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, Filter
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.methods import DeleteMessage, EditMessageText
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from Keyboards.Expense.category import (TodayCallback, ChooseCategoryCallback,
                                        create_today_kb, category_choose_kb)

from Keyboards.Expense.types import create_type_kb, ChooseTypeCallback, BackToCategoriesCallback

from create_bot import bot

from Database.create_database import Expense as ExpenseDB

expensesRouter = Router()


class CheckDate(Filter):
    def __init__(self, date: str) -> None:
        self.date = date

    async def __call__(self, message: Message) -> bool:
        self.date = message.text

        try:
            valid_date = time.strptime(self.date, '%d.%m.%y')

            # Проверка года
            if not (2022 <= valid_date.tm_year <= 2030):
                return True  # Год не входит в диапазон от 2022 до 2030

            # Преобразование введенной даты в объект datetime
            input_datetime = datetime(valid_date.tm_year, valid_date.tm_mon, valid_date.tm_mday)

            # Получение текущей даты
            current_datetime = datetime.now()

            # Проверка, что введенная дата не больше текущей
            if input_datetime > current_datetime:
                return True  # Введенная дата больше текущей даты

        except ValueError:
            return True  # Некорректный формат даты

        return False  # Дата прошла все проверки


class CheckAmount(Filter):
    def __init__(self, amount: str) -> None:
        self.amount = amount

    async def __call__(self, message: Message) -> bool:
        self.amount = message.text

        if ',' in self.amount:
            try:
                # Проверка, что число больше нуля
                print(float(self.amount.replace(',', '.')))
                return not (float(self.amount.replace(',', '.')) > 0.0)
            except ValueError:
                return True
        elif '.' in self.amount:
            return True  # Встречена точка, возвращаем True
        else:
            try:
                print(float(self.amount))
                # Проверка, что число больше нуля
                return not (float(self.amount) > 0.0)
            except ValueError:
                return True  # Встречены буквы или другие символы, возвращаем True


class Expense(StatesGroup):
    date_message_id = State()
    date = State()
    category = State()
    type = State()
    amount = State()
    comment = State()


@expensesRouter.message(Command("expense"))
@expensesRouter.message(F.text.casefold() == "расход")
async def start_messaging(message: Message, state: FSMContext) -> None:
    sent_message = await message.answer(text="Выберете дату расхода:",
                                        reply_markup=create_today_kb())
    await state.update_data(date_message_id=sent_message.message_id)
    await state.set_state(Expense.date)


@expensesRouter.message(Command("cancel_expense"))
@expensesRouter.message(F.text.casefold() == "отмена расхода")
async def delete_expense_adding(message: Message, state: FSMContext) -> None:
    await message.answer(text="Добавление расхода отменено")
    await state.clear()


@expensesRouter.callback_query(Expense.date, TodayCallback.filter())
async def change_date(query: CallbackQuery, callback_data: TodayCallback, state: FSMContext):
    await state.set_state(Expense.date)
    date = callback_data.today
    await query.answer(f"Выбрана дата: {date}")
    await query.message.edit_text(f"Выбрана дата: {date}", reply_markup=None)

    await state.update_data(date=date)

    await query.message.answer(text="Выберите категорию:", reply_markup=category_choose_kb())
    await state.set_state(Expense.category)


@expensesRouter.message(Expense.date, CheckDate(F.text))
async def invalid_date_format(message: Message, state: FSMContext):
    await message.answer(text="Дата должна быть от 2022 до 2030 и не позднее сегодняшнего дня. 📅 Повторите:")
    await state.set_state(Expense.date)


@expensesRouter.message(Expense.date)
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


@expensesRouter.callback_query(Expense.category, ChooseCategoryCallback.filter())
async def set_category(query: CallbackQuery, callback_data: ChooseCategoryCallback, state: FSMContext):
    await query.answer()

    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_text(text=f'Выбрана категория "{category_name}". Выберите тип:',
                                  reply_markup=create_type_kb(category_id))
    await state.set_state(Expense.type)


@expensesRouter.callback_query(Expense.type, BackToCategoriesCallback.filter(F.back == True))
async def back_to_categories(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.edit_text(text="Выберите категорию:", reply_markup=category_choose_kb())
    await state.set_state(Expense.category)


@expensesRouter.callback_query(Expense.type, ChooseTypeCallback.filter())
async def set_category(query: CallbackQuery, callback_data: ChooseTypeCallback, state: FSMContext):
    await query.answer()

    category_id = callback_data.category_id
    category_name = callback_data.category_name

    type_id = callback_data.type_id
    type_name = callback_data.type_name

    await state.update_data(category={"category_id": category_id, "category_name": category_name},
                            type={"type_id": type_id, "type_name": type_name})
    await query.message.edit_text(text=f'Выбран тип "{type_name}" в категории "{category_name}"')
    await query.message.answer(text="Введите сумму расхода:")

    await state.set_state(Expense.amount)


@expensesRouter.message(Expense.amount, CheckAmount(F.text))
async def incorrect_amount(message: Message, state: FSMContext):
    await message.answer("Введено недопустимое значение.")
    await state.set_state(Expense.amount)


@expensesRouter.message(Expense.amount)
async def set_amount(message: Message, state: FSMContext):
    amount = float(message.text.replace(',', '.'))
    await state.update_data(amount=amount)

    await message.answer(text="Введите комментарий")

    await state.set_state(Expense.comment)


@expensesRouter.message(Expense.comment)
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
