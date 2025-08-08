import requests
from src.utils.find_name_flower import get_russian_name_from_latin

def handle_photo(files, ai_token : str):
    try:
        headers = {'Api-Key': ai_token}
        response = requests.post("https://api.plant.id/v3/identification", files=files, headers=headers)
        response.raise_for_status()
        print(response.json())
        response_json = response.json()
        if 'result' in response_json and 'classification' in response_json['result'] and 'suggestions' in response_json['result']['classification']:
            suggestions = response_json['result']['classification']['suggestions']
            if suggestions:
                top_suggestion = suggestions[0]
                plant_name = top_suggestion.get('name', '')
                probability = top_suggestion.get('probability', '')
                try:
                    probability = round(float(probability * 100))
                    if probability < 5:
                        plant_name = ""
                except ValueError:
                    probability = ""
                if probability:
                    response_text = f"Вероятнее всего это: {get_russian_name_from_latin(plant_name, "ru")}\tНаучное название: {plant_name}\n(Вероятность: {probability}%)"
                else: response_text = "Не удалось определить растение."
            else:
                response_text = "Не удалось определить растение."
        else:
            response_text = "Не удалось получить информацию о растении."
        return response_text
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Ошибка запроса к нейронке:\n{e}"
    except Exception as e:
        print(e)
        return f"Неожиданная ошибка:\n{e}"
