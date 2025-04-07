import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_chatgpt_response(prompt: str) -> str:
    """
    Отправляет запрос в OpenAI и возвращает сгенерированный код.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Можно заменить на "gpt-4" при необходимости
        messages=[
            {"role": "system", "content": "Ты профессионал-программист, ведущий специалист крупной компании. Отвечай только кодом."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()
