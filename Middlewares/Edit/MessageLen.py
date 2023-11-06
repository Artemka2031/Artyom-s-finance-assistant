from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.methods import DeleteMessage, SendMessage, EditMessageReplyMarkup
from aiogram.types import Message

from Keyboards.Edit.category import create_category_choose_kb
from Keyboards.Edit.type import create_type_choose_kb
from create_bot import bot

MAX_LEN = 17


class LimitTypeLenMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        limit_len_flag = get_flag(data, "limit_len")
        if limit_len_flag is None:
            return await handler(event, data)

        try:
            chat_id = event.chat.id
            message_id = event.message_id
            state = data["state"]

            state_data = (await state.get_data())

            print(state_data)
            sent_message = state_data["sent_message"]
            query_message = state_data["query_message"]
            category_id = state_data["category_id"]
            message_text = event.text

            print(message_text)
            print(len(message_text))

            if len(message_text) >= MAX_LEN:
                await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))
                await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
                await bot(EditMessageReplyMarkup(chat_id=chat_id,
                                                 message_id=query_message,
                                                 reply_markup=create_type_choose_kb(category_id)))
                await bot(SendMessage(chat_id=chat_id, text="Введённое значение слишком длинное."))
                await state.clear()
                return
        except:
            pass

        return await handler(event, data)


class LimitCategoryLenMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        limit_len_flag = get_flag(data, "limit_category_len")
        if limit_len_flag is None:
            return await handler(event, data)

        try:
            chat_id = event.chat.id
            message_id = event.message_id
            state = data["state"]

            state_data = (await state.get_data())

            print(state_data)
            sent_message = state_data["sent_message"]
            query_message = state_data["query_message"]
            message_text = event.text

            print(message_text)
            print(len(message_text))

            if len(message_text) >= MAX_LEN:
                await bot(DeleteMessage(chat_id=chat_id, message_id=sent_message))
                await bot(DeleteMessage(chat_id=chat_id, message_id=message_id))
                await bot(EditMessageReplyMarkup(chat_id=chat_id,
                                                 message_id=query_message,
                                                 reply_markup=create_category_choose_kb()))
                await bot(SendMessage(chat_id=chat_id, text="Введённое значение слишком длинное."))
                await state.clear()
                return
        except:
            pass

        return await handler(event, data)
