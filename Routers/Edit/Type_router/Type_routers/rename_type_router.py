from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods import DeleteMessage, EditMessageText
from aiogram.types import CallbackQuery, Message
from peewee import IntegrityError

from Database.create_database import ExpenseType
from Keyboards.Edit.type import RenameTypeCallback, CancelTypeRenameCallback, create_edit_type_kb, create_type_choose_kb
from Middlewares.Edit.MessageLen import LimitTypeLenMiddleware
from create_bot import bot

renameTypeRouter = Router()


# Переименование типов
class RenameType(StatesGroup):
    query_message = State()
    category_id = State()
    type_id = State()
    category_name = State()
    type_name = State()
    sent_message = State()
    new_type_name = State()


@renameTypeRouter.callback_query(RenameTypeCallback.filter())
async def rename_type_action(query: CallbackQuery, callback_data: RenameTypeCallback, state: FSMContext):
    await query.answer()

    await state.set_state(RenameType.query_message)

    query_message_id = query.message.message_id
    category_id = callback_data.category_id
    type_id = callback_data.type_id
    type_name = callback_data.type_name
    category_name = callback_data.category_name

    await query.message.edit_reply_markup(reply_markup=create_edit_type_kb(category_id=category_id, type_id=type_id,
                                                                           action=RenameTypeCallback.__prefix__))

    message = await query.message.answer(text=f'Переименуйте тип "{type_name}" \nв категории "{category_name}":')

    await state.update_data(query_message=query_message_id, category_id=category_id, type_id=type_id,
                            type_name=type_name, category_name=category_name, sent_message=message.message_id)
    await state.set_state(RenameType.new_type_name)


@renameTypeRouter.callback_query(RenameType.new_type_name,
                                 CancelTypeRenameCallback.filter((F.cancel == True)))
async def cancel_rename_type(query: CallbackQuery, state: FSMContext):
    await query.answer()
    chat_id = query.message.chat.id

    data = (await state.get_data())
    category_id = data["category_id"]
    type_id = data["type_id"]
    sent_message = data["sent_message"]

    await state.clear()

    await query.message.edit_reply_markup(reply_markup=create_edit_type_kb(category_id, type_id))
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))


renameTypeRouter.message.middleware(LimitTypeLenMiddleware())


@renameTypeRouter.message(RenameType.new_type_name, flags={"limit_len": True})
async def rename_type(message: Message, state: FSMContext):
    chat_id = message.chat.id

    data = await state.get_data()
    new_type_name = message.text

    category_id = data["category_id"]
    type_id = data["type_id"]

    category_name = data["category_name"]
    type_name = data["type_name"]

    query_message = data["query_message"]
    sent_message = data["sent_message"]

    await state.clear()

    await message.delete()
    await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))

    try:
        ExpenseType.rename_type(category_id, type_id, new_type_name)
        await bot(EditMessageText(chat_id=chat_id, message_id=query_message,
                                  text=f'Выберите тип для изменения \nв категории: "{category_name}":',
                                  reply_markup=create_type_choose_kb(category_id=category_id)))
    except IntegrityError:
        await message.answer(text=f'Тип "{new_type_name}" уже есть в категории "{category_name}"')
        await bot(EditMessageText(chat_id=chat_id, message_id=query_message,
                                  text=f'Выберите действие по изменению типа'
                                       f'"{type_name}" в категории "{category_name}":',
                                  reply_markup=create_edit_type_kb(category_id, type_id)))
