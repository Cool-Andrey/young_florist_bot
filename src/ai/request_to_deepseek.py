import aiohttp

async def ask_deepseek_about_flower_disease(
    access_token: str,
    disease: str,
    flower: str,
    language: str = 'ru'
) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    if language == 'ru':
        prompt = (
            f"Ты опытный садовод. Объясни, как лечить заболевание '{disease}' у растения '{flower}'. "
            "Опиши симптомы, возможные причины и пошаговое лечение. "
            "Ответь подробно, но понятно, на русском языке."
        )
    else:
        prompt = (
            f"You are an experienced gardener. Explain how to treat the disease '{disease}' in the plant '{flower}'. "
            "Describe symptoms, possible causes, and step-by-step treatment. "
            f"Respond in {language}."
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
        "max_tokens": 1024,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Ошибка API DeepSeek: {response.status}, {text}")

                data = await response.json()

                # Извлекаем ответ модели
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception("Нет ответа от модели")

    except aiohttp.ClientError as e:
        raise Exception(f"Ошибка сети при обращении к DeepSeek: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при обращении к DeepSeek: {e}")