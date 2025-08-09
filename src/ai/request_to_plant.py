import json

import requests
from src.utils.find_name_flower import get_russian_name_from_latin

def handle_photo(photo, language : str, ai_token : str) -> (str, str | None):
    try:
        plant_id = ""
        data = {
            'images' : [photo],
        }
        details = "common_names, description, taxonomy, synonyms, edible_parts, propagation_methods, watering, best_watering, best_light_condition, best_soil_type, common_uses, toxicity, cultural_significance"
        headers = {'api-key': ai_token}
        response = requests.post(f"https://api.plant.id/v3/identification?details={details}&language={language}", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        print(response_json)
        if 'result' in response_json and 'classification' in response_json['result'] and 'suggestions' in response_json['result']['classification']:
            suggestions = response_json['result']['classification']['suggestions']
            if suggestions:
                top_suggestion = suggestions[0]
                plant_name = top_suggestion.get('name', '')
                probability = top_suggestion.get('probability', '')
                try:
                    probability = round(float(probability * 100))
                    if probability < 5:
                        return "Не удалось определить растение.", None
                except (ValueError, TypeError):
                    return "Не удалось определить растение.", None
                russian_name = get_russian_name_from_latin(plant_name, "ru")
                details = top_suggestion.get('details', {})
                description = details.get('description', '')
                edible_parts = details.get('edible_parts', [])
                toxicity = details.get('toxicity', '')
                common_names = details.get('common_names', [])
                lines = [
                    f"Вероятнее всего это: {russian_name}",
                    f"Научное название: {plant_name}"
                ]
                if common_names:
                    lines.append(f"Другие названия: {', '.join(common_names)}")
                lines.append(f"(Вероятность: {probability}%)")
                if description:
                    lines.append(f"\nОписание: {description}")
                if edible_parts:
                    lines.append(f"Съедобные части: {', '.join(edible_parts)}")
                if toxicity:
                    lines.append(f"Токсичность: {toxicity}")
                response_text = "\n".join(lines)
                return response_text, response_json['access_token']
            else:
                return "Не удалось определить растение.", None
        else:
            return "Не удалось получить информацию о растении.", None
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Ошибка запроса к нейронке:\n{e}", None
    except Exception as e:
        print(e)
        return f"Неожиданная ошибка:\n{e}", None

def get_details(access_token : str, ai_token : str) -> str:
    try:
        headers = {'api-key': ai_token}
        response = requests.get(f"https://api.plant.id/v3/identification/{access_token}", headers)
        response.raise_for_status()
        response_json = response.json()
        formatted_json = json.dumps(response_json, ensure_ascii=False, indent=2)
        print(formatted_json)
        return formatted_json
    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"ошибка запроса к нейронке:\n{e}")
    except Exception as e:
        print(e)
        raise Exception(f"Неожиданная ошибка:\n{e}")
