from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import DeleteMessage
from aiogram.types import CallbackQuery

from Database.create_database import ExpenseCategory
from Keyboards.Edit.category import create_category_choose_kb
from Keyboards.Edit.type import DeleteCategoryCallback, CancelCategoryDeleteCallback, create_type_choose_kb
from create_bot import bot

deleteCategoryRouter = Router()


# Удаление категории
class DeleteCategory(StatesGroup):
    query_message = State()
    category_id = State()
    category_name = State()
    confirm = State()


@deleteCategoryRouter.callback_query(DeleteCategoryCallback.filter(), flags={"delete_sent_message": True})
async def delete_category_action(query: CallbackQuery, callback_data: DeleteCategoryCallback, state: FSMContext):
    await query.answer()

    await state.set_state(DeleteCategory.query_message)

    query_message_id = query.message.message_id
    category_id = callback_data.category_id
    category_name = callback_data.category_name

    await query.message.edit_reply_markup(reply_markup=create_type_choose_kb(category_id=category_id,
                                                                             delete_category=True))

    await state.update_data(query_message=query_message_id, category_id=category_id, category_name=category_name)
    await state.set_state(DeleteCategory.confirm)


@deleteCategoryRouter.callback_query(DeleteCategory.confirm,
                                     CancelCategoryDeleteCallback.filter(F.cancel_delete_category == True))
async def cancel_delete_category_action(query: CallbackQuery, state: FSMContext):
    await query.answer()

    data = (await state.get_data())
    category_id = data["category_id"]

    await state.clear()

    await query.message.edit_reply_markup(reply_markup=create_type_choose_kb(category_id))


@deleteCategoryRouter.callback_query(DeleteCategory.confirm,
                                     CancelCategoryDeleteCallback.filter(F.cancel_delete_category == False))
async def delete_category(query: CallbackQuery, state: FSMContext):
    data = (await state.get_data())
    category_id = data["category_id"]
    category_name = data["category_name"]

    await state.clear()

    ExpenseCategory.delete_category(category_id=category_id)
    await query.answer(text=f'Категория "{category_name}" была удалён')
    await query.message.edit_text(text=f'Выберите категорию для изменения":',
                                  reply_markup=create_category_choose_kb())
