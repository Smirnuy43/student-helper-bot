from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class UserState(StatesGroup):
    choosing_language = State()
    waiting_for_task = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Я бот-помощник по программированию.\n\n"
        "Давай начнем! Выбери язык программирования:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Python"), KeyboardButton(text="C++")],
                [KeyboardButton(text="C"), KeyboardButton(text="C#")],
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(UserState.choosing_language)

@router.message(UserState.choosing_language)
async def language_chosen(message: Message, state: FSMContext):
    language = message.text.strip()
    await state.update_data(language=language)
    await state.set_state(UserState.waiting_for_task)

    await message.answer(
        f"✅ Язык выбран: {language}\nТеперь пришли мне условие задачи — текстом или файлом.",
        reply_markup=None
    )
