from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...common.services.user_info_service import update_user_info
from ...config import GROUP_ID, get_bot

router = Router()


class Form(StatesGroup):
    support_question = State()
    answer = State()


@router.message(Form.support_question)
async def send_question_to_support_group(message: Message, state: FSMContext):
    data = await state.get_data()
    language_code = data["language_code"]
    user_id = message.from_user.id
    bot = await get_bot()

    await message.reply(
        "Your question was sent"
        if language_code == "en"
        else "Ваше питання було відправлено"
    )

    markup = InlineKeyboardBuilder()
    markup.button(
        text="💬 Answer",
        callback_data=f"s_answer:{message.chat.id}:{user_id}:{message.message_id}",
    )

    markup.button(
        text="❌ Ignore",
        callback_data=f"s_ignore:{message.chat.id}:{user_id}:{message.message_id}",
    )
    markup.adjust(1, 1)

    if language_code == "en":
        caption = f'<b>New question was taken!</b>\n <b>From:</b> {message.from_user.first_name}\nID: {message.chat.id}\n<b>Message:</b> "{message.text}'

    else:
        caption = f'<b>Нове питання було взято!</b>\n<b>Від:</b> {message.from_user.first_name}\nID: {message.chat.id}\n<b>Повідомлення:</b> "{message.text}"'

    await bot.send_message(
        int(GROUP_ID),
        caption,
        reply_markup=markup.as_markup(),
        parse_mode="HTML",
    )

    await update_user_info(user_id, is_support_pending=True)

    await bot.session.close()
    await state.clear()


async def answer_message(
    message_id,
    chat_id: int,
    user_id: int,
    question_message_id: int,
    state: FSMContext,
    language_code: str,
):
    bot = await get_bot()
    await bot.send_message(
        GROUP_ID,
        "Enter your answer: " if language_code == "en" else "Введіть вашу відповідь",
    )
    await state.set_state(Form.answer)
    await state.update_data(
        chat_id=chat_id,
        user_id=user_id,
        question_message_id=question_message_id,
        message_id=message_id,
        language_code=language_code,
    )

    await bot.session.close()


@router.message(Form.answer)
async def send_answer(message: Message, state: FSMContext):
    bot = await get_bot()
    data = await state.get_data()
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    question_message_id = data.get("question_message_id")
    message_id = data.get("message_id")
    language_code = data.get("language_code")

    await bot.send_message(
        chat_id,
        (
            f"You have received an answer:\n<b>{message.text}</b>"
            if language_code == "en"
            else f"Ви отримали відповідь:\n<b>{message.text}</b>"
        ),
        parse_mode="HTML",
        reply_to_message_id=question_message_id,
    )
    await message.reply(
        "Your answer was sent"
        if language_code == "en"
        else "Ваша відповідь була відправлена"
    )
    await update_user_info(user_id, is_support_pending=False)
    await bot.delete_message(GROUP_ID, message_id)
    await state.clear()

    await bot.session.close()


async def ignore_message(
    message_id,
    chat_id: int,
    user_id: int,
    question_message_id: int,
    language_code: str,
):
    bot = await get_bot()
    await bot.send_message(
        chat_id,
        (
            "Unfortunately, your question was denied"
            if language_code == "en"
            else "На жаль, ваше питання було відхилено"
        ),
        reply_to_message_id=question_message_id,
    )

    await bot.delete_message(GROUP_ID, message_id)
    await update_user_info(user_id, is_support_pending=False)
    await bot.session.close()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
