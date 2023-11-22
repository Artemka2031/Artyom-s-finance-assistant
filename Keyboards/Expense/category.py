from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Database.create_database import ExpenseCategory, ExpenseType


class TodayCallback(CallbackData, prefix="TDC"):
    today: str


class CategoryChooseCallback(CallbackData, prefix="CC"):
    pass


class TypeChooseCallback(CallbackData, prefix="TC"):
    pass


class AmountSetCallback(CallbackData, prefix="AS"):
    pass


BASE_COMMENT = "Установить комментарий"


class CommentSetCallback(CallbackData, prefix="CS"):
    pass


def create_today_kb():
    today = datetime.today().strftime('%d.%m.%y')
    text = "Сегодня"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=TodayCallback(today=today).pack())
    return builder.as_markup()

# def create_date_button(date: str):
#     today = datetime.today().strftime('%d.%m.%y')
#     text = "Сегодня" if date == today else today
#     return InlineKeyboardButton(text=text, callback_data=TodayCallback().pack())
#
#
# def create_category_button(category_id):
#     category_name = ExpenseCategory.get_category_name(category_id) if category_id != 0 else "Категория"
#     return InlineKeyboardButton(text=category_name, callback_data=CategoryChooseCallback().pack())
#
#
# def create_type_button(category_id, type_id):
#     if category_id == 0:
#         return None
#
#     if type_id == 0:
#         return InlineKeyboardButton(text="Тип", callback_data=TypeChooseCallback().pack())
#
#     type_name = ExpenseType.get_type_name(category_id, type_id)
#     return InlineKeyboardButton(text=type_name, callback_data=CategoryChooseCallback().pack())
#
#
# def create_amount_button(amount):
#     amount = amount if amount != 0 else "Сумма"
#     return InlineKeyboardButton(text=amount, callback_data=AmountSetCallback().pack())
#
#
# def create_comment_button(comment):
#     comment = comment if comment == BASE_COMMENT else "Комментарий установлен"
#     return InlineKeyboardButton(text=comment, callback_data=CommentSetCallback().pack())
#

# def add_expense_kb(date: str, category_id: int = 0, type_id: int = 0,
#                    amount: float = 0, comment: str = BASE_COMMENT):
#     expenseB = InlineKeyboardBuilder()
#
#     buttons = [
#         create_date_button(date),
#         create_category_button(category_id),
#         create_type_button(category_id, type_id),
#         create_amount_button(amount),
#         create_comment_button(comment)
#     ]
#
#     for button in buttons:
#         if button is not None:
#             expenseB.add(button)
#
#     expenseB.adjust(1, 2)
#
#     return expenseB.as_markup()
