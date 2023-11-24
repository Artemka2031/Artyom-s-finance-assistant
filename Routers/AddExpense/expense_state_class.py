from aiogram.fsm.state import StatesGroup, State


class Expense(StatesGroup):
    date_message_id = State()
    date = State()
    category = State()
    type = State()
    amount = State()
    comment = State()
