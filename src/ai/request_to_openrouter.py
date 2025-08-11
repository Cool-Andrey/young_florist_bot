import aiohttp
from typing import List

async def ask_openrouter_about_flower_diseases(
        api_key: str,
        diseases: List[str],
        flower: str,
        language: str = 'ru',
        model: str = "mistralai/mistral-7b-instruct:free"  # Бесплатная модель по умолчанию
) -> str:
    """
    Запрашивает информацию о болезнях растений через OpenRouter API.

    Args:
        api_key: Ключ API из https://openrouter.ai/keys
        diseases: Список предполагаемых болезней
        flower: Название растения
        language: Язык ответа ('ru' или другой)
        model: Модель ИИ (список доступных: https://openrouter.ai/models)

    Returns:
        Структурированный ответ с описанием болезней
    """
    if not diseases:
        raise ValueError("Список болезней не может быть пустым")

    # Формируем список болезней с нумерацией
    diseases_list = "\n".join(f"{i+1}. {disease}" for i, disease in enumerate(diseases))

    # Подготовка промпта (адаптировано под русский язык)
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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://flower-disease-checker.local",  # Требуется OpenRouter
        "X-Title": "Flower Disease Checker",                   # Требуется OpenRouter
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1200,  # Рекомендуется для бесплатных моделей
    }

    url = "https://openrouter.ai/api/v1/chat/completions"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                # Обработка специфичных ошибок OpenRouter
                if response.status == 402:
                    error_data = await response.json()
                    raise ValueError(
                        "Недостаточно средств: "
                        "1. Проверьте баланс на https://openrouter.ai/account/keys\n"
                        "2. Используйте бесплатные модели (с :free в названии)"
                    )

                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Ошибка API OpenRouter ({response.status}): {error_text}")

                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()

    except aiohttp.ClientError as e:
        raise ConnectionError(f"Сетевая ошибка: {str(e)}")
    except KeyError:
        raise ValueError("Некорректный ответ от API. Проверьте модель и структуру запроса")
