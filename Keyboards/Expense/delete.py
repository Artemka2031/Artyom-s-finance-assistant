from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DeleteExpense(CallbackData, prefix="DelE"):
    expense_id: int
    delete: bool


class ConfirmDeleteExpense(CallbackData, prefix="ConfDE"):
    expense_id: int
    confirm_delete: bool


def create_delete_expense_kb(expense_id: int, confirm: bool):
    delete_b = InlineKeyboardBuilder()

    if not confirm:
        delete_b.button(text="Удалить", callback_data=DeleteExpense(expense_id=expense_id, delete=True).pack())
    else:
        delete_b.button(text="Удалить",
                        callback_data=ConfirmDeleteExpense(expense_id=expense_id, confirm_delete=True).pack())
        delete_b.button(text="Отмена",
                        callback_data=ConfirmDeleteExpense(expense_id=expense_id, confirm_delete=False).pack())

    return delete_b.as_markup()
