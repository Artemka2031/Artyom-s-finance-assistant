from aiogram import Router
from aiogram.types import CallbackQuery
from magic_filter import F

from Database.Tables.ExpensesTables import ExpenseType, ExpenseCategory
from Keyboards.Edit.category import ChooseCategoryEditCallback
from Keyboards.Edit.type import create_type_choose_kb
from .Category_routers import deleteCategoryRouter, newCategoryRouter, renameCategoryRouter

categoryEditRouter = Router()


@categoryEditRouter.callback_query(ChooseCategoryEditCallback.filter(F.operation == "expense"),
                                   flags={"delete_sent_message": True})
async def edit_category_callback(query: CallbackQuery, callback_data: ChooseCategoryEditCallback):
    await query.answer()

    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_text(text=f'Выберите тип для изменения \nв категории "{category_name}":',
                                  reply_markup=create_type_choose_kb(category_id, OperationType=ExpenseType,
                                                                     OperationCategory=ExpenseCategory))


# Добавляем роутер по изменению имени категории
categoryEditRouter.include_router(renameCategoryRouter)

# Добавляем роутер по удалению категории
categoryEditRouter.include_router(deleteCategoryRouter)

# Добавляем роутер по добавлению новой категории
categoryEditRouter.include_router(newCategoryRouter)
