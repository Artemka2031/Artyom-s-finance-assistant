from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import inline_keyboard_button as ik

from Database.create_database import ExpenseType, ExpenseCategory


class BaseTypeCallbackData(CallbackData, prefix="Base T Callback"):
    category_id: int
    category_name: str
    type_id: int
    type_name: str


class BaseCategoryCallbackData(CallbackData, prefix="Base C Callback"):
    category_id: int
    category_name: str


class ChooseTypeEditCallback(BaseTypeCallbackData, prefix="Choose T"):
    pass


class NewTypeCallback(CallbackData, prefix="New T"):
    category_id: int
    create: bool


class BackToCategoriesEditCallback(CallbackData, prefix="Back to C"):
    back: bool


class RenameCategoryCallback(BaseCategoryCallbackData, prefix="Rename C"):
    pass


class CancelCategoryRenameCallback(BaseCategoryCallbackData, prefix="Cansel Rename C"):
    cancel_rename_category: bool


class DeleteCategoryCallback(BaseCategoryCallbackData, prefix="Delete C"):
    pass


class CancelCategoryDeleteCallback(CallbackData, prefix="Cancel Delete C"):
    cancel_delete_category: bool


def create_type_choose_kb(category_id: int, create: bool = True,
                          rename_category: bool = False, delete_category: bool = False):
    chooseTypeB = InlineKeyboardBuilder()

    types = ExpenseType.get_all_types(category_id)
    category_name = ExpenseCategory.get_category_name(category_id)

    for type_dic in types:
        category_id = int(type_dic["category_id"])
        category_name = type_dic["category_name"]

        type_id = int(type_dic["type_id"])
        type_name = type_dic["type_name"]

        chooseTypeB.button(text=type_name,
                           callback_data=ChooseTypeEditCallback(category_id=category_id,
                                                                category_name=category_name,
                                                                type_id=type_id,
                                                                type_name=type_name).pack())
    chooseTypeB.adjust(2)

    back_button = ik.InlineKeyboardButton(text="Категории",
                                          callback_data=BackToCategoriesEditCallback(back=True).pack())

    if create:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Новый тип",
                                                callback_data=NewTypeCallback(category_id=category_id,
                                                                              create=True).pack()),
                        back_button
                        )
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Отменить",
                                                callback_data=NewTypeCallback(category_id=category_id,
                                                                              create=False).pack()),
                        back_button
                        )

    if not rename_category:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Переименовать категорию",
                                                callback_data=RenameCategoryCallback(category_id=category_id,
                                                                                     category_name=category_name).pack()))
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Отмена",
                                                callback_data=CancelCategoryRenameCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_rename_category=True)
                                                .pack()))

    if not delete_category:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Удалить категорию",
                                                callback_data=DeleteCategoryCallback(category_id=category_id,
                                                                                     category_name=category_name).pack()))
    else:
        chooseTypeB.row(ik.InlineKeyboardButton(text="Удалить",
                                                callback_data=CancelCategoryDeleteCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_delete_category=False)
                                                .pack()),
                        ik.InlineKeyboardButton(text="Отмена",
                                                callback_data=CancelCategoryDeleteCallback(category_id=category_id,
                                                                                           category_name=category_name,
                                                                                           cancel_delete_category=True)
                                                .pack()))

    return chooseTypeB.as_markup()


class BackToTypesCallback(CallbackData, prefix="Back to T"):
    category_id: int
    back: bool


class RenameTypeCallback(BaseTypeCallbackData, prefix="Rename T"):
    pass


class CancelTypeRenameCallback(CallbackData, prefix="Cansel Rename T"):
    cancel: bool


class DeleteTypeCallback(BaseTypeCallbackData, prefix="Delete type"):
    pass


class CancelTypeDeleteCallback(CallbackData, prefix="Cansel Rename T"):
    cancel_delete: bool


class MoveTypeCallback(BaseTypeCallbackData, prefix="Move type", ):
    pass


def create_edit_type_kb(category_id: int, type_id: int, action: str = "Default"):
    type_expense = ExpenseType.get_type(category_id, type_id)

    category_id = int(type_expense["category_id"])
    category_name = type_expense["category_name"]
    type_id = int(type_expense["type_id"])
    type_name = type_expense["type_name"]

    editTypeB = InlineKeyboardBuilder()

    def create_button(CallbackClass, button_text):
        editTypeB.button(text=button_text,
                         callback_data=CallbackClass(category_id=category_id,
                                                     category_name=category_name,
                                                     type_id=type_id,
                                                     type_name=type_name).pack())

    if action == RenameTypeCallback.__prefix__:
        editTypeB.button(text="Отмена",
                         callback_data=CancelTypeRenameCallback(cancel=True).pack())
    elif action == DeleteTypeCallback.__prefix__:
        editTypeB.button(text="Удалить тип",
                         callback_data=CancelTypeDeleteCallback(cancel_delete=False).pack())
        editTypeB.button(text="Отмена",
                         callback_data=CancelTypeDeleteCallback(cancel_delete=True).pack())
    else:
        create_button(RenameTypeCallback, "Переименовать")
        create_button(DeleteTypeCallback, "Удалить тип")
        # create_button(MoveTypeCallback, "Переместить")

        editTypeB.button(text="Типы",
                         callback_data=BackToTypesCallback(category_id=category_id, back=True).pack())

    editTypeB.adjust(2)

    return editTypeB.as_markup()
