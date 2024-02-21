from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import DeleteMessage, EditMessageReplyMarkup
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Database.Tables.ExpensesTables import ExpenseCategory, ExpenseType
from Keyboards.Edit.type import NewTypeCallback, create_type_choose_kb
from Middlewares.Edit.MessageLen import LimitTypeLenMiddleware
from create_bot import bot

newTypeRouter = Router()


# Новые типы
class NewType(StatesGroup):
    query_message = State()
    category_id = State()
    sent_message = State()
    type_name = State()


@newTypeRouter.callback_query(NewTypeCallback.filter(F.create == True), flags={"delete_sent_message": True})
async def new_type_callback(query: CallbackQuery, callback_data: NewTypeCallback, state: FSMContext):
    await query.answer()

    await state.set_state(NewType.query_message)

    category_id = callback_data.category_id
    await state.update_data(category_id=category_id)
    await query.message.edit_reply_markup(
        reply_markup=create_type_choose_kb(category_id=category_id, OperationType=ExpenseType,
                                           OperationCategory=ExpenseCategory, create=False))

    query_message_id = query.message.message_id
    await state.set_state(NewType.query_message)
    await state.update_data(query_message=query_message_id)

    message = await query.message.answer(text=f"Напишите название нового типа:")
    await state.set_state(NewType.sent_message)
    await state.update_data(sent_message=message.message_id)

    await state.set_state(NewType.type_name)


@newTypeRouter.callback_query(NewType.type_name, NewTypeCallback.filter(F.create == False))
async def cancel_new_type_callback(query: CallbackQuery, state: FSMContext, callback_data: NewTypeCallback):
    chat_id = query.message.chat.id

    category_id = callback_data.category_id
    category_name = ExpenseCategory.get_name_by_id(category_id)
    sent_message = (await state.get_data())["sent_message"]

    await query.answer()
    await state.clear()

    await query.message.edit_text(text=f'Выберите тип для изменения в категории: "{category_name}"',
                                  reply_markup=create_type_choose_kb(category_id, OperationType=ExpenseType,
                                                                     OperationCategory=ExpenseCategory))

    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))


newTypeRouter.message.middleware(LimitTypeLenMiddleware())


@newTypeRouter.message(NewType.type_name, flags={"limit_len": True})
async def add_new_type(message: Message, state: FSMContext):
    chat_id = message.chat.id
    message_id = message.message_id
    type_name = message.text

    await state.update_data(type_name=type_name)

    data = await state.get_data()
    category_id = data['category_id']
    category_name = ExpenseCategory.get_name_by_id(category_id)
    sent_message_id = data['sent_message']
    query_message_id = data['query_message']

    await state.clear()

    try:
        ExpenseType.add_type(type_name, category_id)
    except IntegrityError:
        await message.answer(text=f"Тип с именем '{type_name}' уже существует в категории '{category_name}'.")

    await bot(EditMessageReplyMarkup(chat_id=chat_id,
                                     message_id=query_message_id,
                                     reply_markup=create_type_choose_kb(category_id, ExpenseType, ExpenseCategory)))
    await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message_id))
