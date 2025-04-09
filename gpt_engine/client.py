import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные среды
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Новый способ инициализации клиента
client = OpenAI(api_key=OPENAI_API_KEY)

def get_chatgpt_response(prompt: str) -> str:
    """
    Отправляет запрос в ChatGPT (GPT-3.5-turbo) и возвращает ответ.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты помощник-программист. Отвечай только кодом."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()
