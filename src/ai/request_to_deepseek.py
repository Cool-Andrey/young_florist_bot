import aiohttp
from typing import List

async def ask_deepseek_about_flower_diseases(
        access_token: str,
        diseases: List[str],
        flower: str,
        language: str = 'ru'
) -> str:
    if not diseases:
        raise Exception("Список болезней пуст.")

    # Формируем список болезней с нумерацией
    diseases_list = "\n".join(f"{i+1}. {disease}" for i, disease in enumerate(diseases))

    if language == 'ru':
        prompt = (
            f"Ты опытный садовод. Пользователь подозревает, что у растения '{flower}' есть одна или несколько проблем. "
            f"Наиболее вероятные заболевания в порядке убывания вероятности:\n"
            f"{diseases_list}\n\n"
            "Для каждого заболевания подробно опиши:\n"
            "- Характерные симптомы\n"
            "- Основные причины возникновения\n"
            "- Пошаговые рекомендации по лечению и восстановлению растения\n\n"
            "Ответ должен быть структурированным, понятным для начинающих цветоводов и на русском языке."
        )
    else:
        prompt = (
            f"You are an experienced gardener. A user suspects their plant '{flower}' has one or more issues. "
            f"The most likely diseases in descending order of probability:\n"
            f"{diseases_list}\n\n"
            "For each disease, please describe:\n"
            "- Key symptoms\n"
            "- Main causes\n"
            "- Step-by-step treatment and recovery advice\n\n"
            f"Provide a well-structured, beginner-friendly response in {language}."
        )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1500,  # Увеличили, чтобы вместить все 3 болезни
    }
    url = "https://api.deepseek.com/v1/chat/completions"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url.strip(), json=payload, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Ошибка API DeepSeek: {response.status}, {text}")

                data = await response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception("Нет ответа от модели")

    except aiohttp.ClientError as e:
        raise Exception(f"Ошибка сети при обращении к DeepSeek: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при обращении к DeepSeek: {e}")
