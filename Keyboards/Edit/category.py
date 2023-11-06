from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import inline_keyboard_button as ik

from Database.create_database import ExpenseCategory, ExpenseType


class ChooseCategoryEditCallback(CallbackData, prefix="Choose C"):
    category_id: int
    category_name: str


class NewCategoryCallback(CallbackData, prefix="New C"):
    create: bool


def create_category_choose_kb(category_create: bool = True):
    chooseCategoryB = InlineKeyboardBuilder()

    categories = ExpenseCategory.get_all_categories()

    for category_dic in categories:
        category_id = int(category_dic["id"])
        category_name = category_dic["name"]

        chooseCategoryB.button(text=category_name,
                               callback_data=ChooseCategoryEditCallback(category_id=category_id,
                                                                        category_name=category_name).pack())
    chooseCategoryB.adjust(2)

    if category_create:
        chooseCategoryB.row(ik.InlineKeyboardButton(text="Новая категория",
                                                    callback_data=NewCategoryCallback(create=True).pack()))
    else:
        chooseCategoryB.row(ik.InlineKeyboardButton(text="Отменить",
                                                    callback_data=NewCategoryCallback(create=False).pack()))

    return chooseCategoryB.as_markup()