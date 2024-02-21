from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from Database.Tables.ExpensesTables import ExpenseCategory
from Keyboards.Edit.category import create_category_choose_kb
from Middlewares.Edit.ClearStateMiddleware import ClearStateMiddleware
from .CategoryRouter import categoryEditRouter
from .TypeRouter import typeEditRouter

editExpenseCategoriesRouter = Router()


# Методы для запуска работы с редактором категорий и типов
@editExpenseCategoriesRouter.message(Command("edit_expense_categories"))
@editExpenseCategoriesRouter.message(F.text.casefold() == "редактирование категорий")
async def start_messaging(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text="Выберите категорию для изменения",
                         reply_markup=create_category_choose_kb(OperationCategory=ExpenseCategory,
                                                                category_create=True))


editExpenseCategoriesRouter.callback_query.middleware(ClearStateMiddleware())

editExpenseCategoriesRouter.include_router(categoryEditRouter)
editExpenseCategoriesRouter.include_router(typeEditRouter)
