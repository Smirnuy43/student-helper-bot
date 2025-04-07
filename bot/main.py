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

# Загрузка конфигурации из .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(storage=MemoryStorage())

# === Обработчик текстовых сообщений ===
@dp.message(lambda m: m.text is not None)
async def handle_text(message: Message):
    try:
        task_text = message.text.strip()

        if len(task_text) < 10:
            await message.answer("⚠️ Пожалуйста, пришлите более подробное описание задачи.")
            return

        prompt = build_prompt(task_text, language="Python")

        await message.answer("🤖 Думаю над решением...")

        result = get_chatgpt_response(prompt)

        await message.answer(f"📦 Готово! Вот решение:\n\n```python\n{result}\n```")

    except Exception as e:
        await message.answer("❌ Ошибка при обработке текста.")
        logging.exception(e)


# === Обработчик документов ===
@dp.message(lambda m: m.document is not None)
async def handle_document(message: Message):
    try:
        file_path = await download_file(bot, message.document)
        await message.answer(f"✅ Файл получен: `{file_path.name}`")

        text = extract_text_from_file(file_path)
        prompt = build_prompt(text, language="Python")

        await message.answer("🤖 Обращаюсь к ИИ, ожидайте...")

        result = get_chatgpt_response(prompt)
        await message.answer(f"📦 Сгенерированный код:\n\n```python\n{result}\n```")

    except ValueError as e:
        await message.answer(f"⚠️ {e}")
    except Exception as e:
        await message.answer("❌ Ошибка при обработке файла или обращении к модели.")
        logging.exception(e)


# === Точка входа ===
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())