import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from file_processor.parser import download_file, extract_text_from_file
from prompt_constructor.constructor import build_prompt
from gpt_engine.client import get_chatgpt_response
from bot.handlers import start
from aiogram import Router
from bot.handlers.start import UserState
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


# Загрузка конфигурации из .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(storage=MemoryStorage())

router = Router()
router.include_routers(start.router)

dp.include_router(router)

# === Обработчик текстовых сообщений ===
@dp.message(UserState.waiting_for_task, lambda m: m.text is not None)
async def handle_text(message: Message, state: FSMContext):
    try:
        task_text = message.text.strip()
        if len(task_text) < 10:
            await message.answer("⚠️ Пожалуйста, пришлите более подробное описание задачи.")
            return

        data = await state.get_data()
        lang = data.get("language", "Python")

        prompt = build_prompt(task_text, language=lang)
        await message.answer("🤖 Думаю над решением...")

        result = get_chatgpt_response(prompt)
        await message.answer(f"📦 Вот решение:\n\n```{lang.lower()}\n{result}\n```")

    except Exception as e:
        await message.answer("❌ Ошибка при обработке текста.")
        logging.exception(e)

# === Обработчик документов ===
@dp.message(UserState.waiting_for_task, lambda m: m.document is not None)
async def handle_document(message: Message, state: FSMContext):
    try:
        # 1. Скачиваем файл
        file_path = await download_file(bot, message.document)
        await message.answer(f"✅ Файл получен: `{file_path.name}`")

        # 2. Парсим содержимое
        text = extract_text_from_file(file_path)
        if not text or len(text.strip()) < 10:
            await message.answer("⚠️ Не удалось извлечь содержимое или оно слишком короткое.")
            return

        # 3. Получаем выбранный язык из состояния
        data = await state.get_data()
        language = data.get("language", "Python")

        # 4. Формируем промпт
        prompt = build_prompt(text, language=language)
        await message.answer("🤖 Думаю над решением...")

        # 5. Отправляем в OpenAI
        result = get_chatgpt_response(prompt)

        # 6. Возвращаем код
        await message.answer(f"📦 Готово! Вот решение:\n\n```{language.lower()}\n{result}\n```")

    except ValueError as e:
        await message.answer(f"⚠️ {e}")
    except Exception as e:
        await message.answer("❌ Ошибка при обработке файла.")
        logging.exception(e)


# === Точка входа ===
async def main():
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())