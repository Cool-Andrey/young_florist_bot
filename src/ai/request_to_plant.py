from typing import Optional

import requests
from aiogram.utils.media_group import MediaGroupBuilder
from deep_translator import GoogleTranslator

from src.utils.utils import get_russian_name_from_latin, format_plant_details, download_similar_images, \
    build_similar_images_media_group, parse_plant_health_response


def handle_photo(photo_base_64: str,
                 ai_token: str,
                 language: str = 'ru'
                 ) -> (str, str | None, str | None):
    try:
        data = {
            'images': [photo_base_64],
            "similar_images": True
        }
        params = {
            'language': language,
            'details': 'common_names,description,taxonomy,synonyms,edible_parts,propagation_methods,watering,best_watering,best_light_condition,best_soil_type,common_uses,toxicity,cultural_significance'
        }
        headers = {'api-key': ai_token}
        response = requests.post("https://api.plant.id/v3/identification",
                                 headers=headers, json=data, params=params)
        response.raise_for_status()
        response_json = response.json()
        if not response_json.get("result", {}).get("is_plant", {}).get("binary", False):
            return "Не обнаружено растение", None

        if 'result' in response_json and 'classification' in response_json['result'] and 'suggestions' in \
                response_json['result']['classification']:
            suggestions = response_json['result']['classification']['suggestions']
            if suggestions:
                top_suggestion = suggestions[0]
                plant_name = top_suggestion.get('name', '')
                probability = top_suggestion.get('probability', 0)

                try:
                    probability_percent = round(float(probability) * 100)
                    if probability_percent < 5:
                        return "Не удалось определить растение.", None
                except (ValueError, TypeError):
                    return "Не удалось определить растение.", None

                details = top_suggestion.get('details', {})
                description = details.get('description', '')
                common_names = details.get('common_names', [])

                lines = [
                    f"Вероятнее всего это: {common_names[0] if common_names else get_russian_name_from_latin(plant_name, language)}",
                    f"Научное название: {plant_name}"
                ]

                if common_names and len(common_names) > 1:
                    lines.append(f"Другие названия: {', '.join(common_names[1:])}")

                lines.append(f"(Вероятность: {probability_percent}%)")

                if description:
                    try:
                        desc_str = str(description) if description is not None else ""
                        translator = GoogleTranslator(source_lang='auto', target=language)
                        translated_desc = translator.translate(desc_str)
                        lines.append(f"\nОписание: {translated_desc}")
                    except Exception as e:
                        desc_preview = str(description)[:30] + "..." if description and len(str(description)) > 30 else str(description)
                        text_error = f"⚠️ Ошибка перевода '{desc_preview}': {str(e)}"
                        print(text_error)
                        lines.append("\nОписание: Не удалось перевести описание.")

                response_text = "\n".join(lines)
                return response_text, response_json['access_token'], plant_name
            else:
                return "Не удалось определить растение.", None, None
        else:
            return "Не удалось получить информацию о растении.", None, None
    except requests.exceptions.RequestException as e:
        print(e)
        return f"Ошибка запроса к нейронке:\n{e}", None, None
    except Exception as e:
        print(e)
        return f"Неожиданная ошибка:\n{e}", None, None


def get_details(
        access_token: str,
        ai_token: str,
        language: str = 'ru'
) -> str:
    try:
        headers = {'api-key': ai_token}
        params = {
            'language': language,
            'details': 'common_names,description,taxonomy,synonyms,edible_parts,propagation_methods,watering,best_watering,best_light_condition,best_soil_type,common_uses,toxicity,cultural_significance,taxonomy'
        }
        response = requests.get(f"https://api.plant.id/v3/identification/{access_token}", headers=headers,
                                params=params)
        response.raise_for_status()
        response_json = response.json()
        if not response_json.get("result", {}).get("is_plant", {}).get("binary", False):
            return "Не обнаружено растение"
        return format_plant_details(response_json, language)
    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"Ошибка запроса к нейронке:\n{e}")
    except Exception as e:
        print(e)
        raise Exception(f"Неожиданная ошибка:\n{e}")


async def get_similar_images(
        access_token: str,
        ai_token: str
) -> Optional[MediaGroupBuilder]:
    try:
        headers = {'api-key': ai_token}
        response = requests.get(f"https://api.plant.id/v3/identification/{access_token}", headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if not response_json.get("result", {}).get("is_plant", {}).get("binary", False):
            return "Не обнаружено растение"
        if 'result' in response_json and 'classification' in response_json['result'] and 'suggestions' in \
                response_json['result']['classification']:
            suggestions = response_json['result']['classification']['suggestions']
            plant_data = suggestions[0]
            plant_name = plant_data["name"]

            common_name = None
            if "details" in plant_data and "common_names" in plant_data["details"] and plant_data["details"][
                "common_names"]:
                common_name = plant_data["details"]["common_names"][0]
            similar_images = plant_data.get("similar_images", [])
            if not similar_images:
                raise Exception("Похожие изображения не найдены для этого растения.")
                return None
            downloaded_images = await download_similar_images(similar_images)
            if not downloaded_images:
                raise Exception("Не удалось загрузить похожие изображения, но я могу рассказать о растении.")
            media_group = build_similar_images_media_group(
                downloaded_images,
                plant_name,
                common_name
            )

            if not media_group:
                raise Exception("Не удалось подготовить медиа-группу с похожими изображениями.")
                return None
            return media_group
    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"Ошибка запроса к нейронке:\n{e}")
    except Exception as e:
        print(e)
        raise Exception(f"Неожиданная ошибка:\n{e}")


def health_check(
        photo_base_64 : str,
        ai_token : str,
        language : str = 'ru'
) -> str:
    try:
        data = {
            'images' : photo_base_64
        }
        headers = {'api-key' : ai_token}
        response = requests.post("https://api.plant.id/v3/health_assessment", headers=headers, json=data)
        response.raise_for_status()
        return parse_plant_health_response(response.json(), language)
    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"Ошибка запроса к нейронке:\n{e}")
    except Exception as e:
        print(e)
        raise Exception(f"Неожиданная ошибка:\n{e}")
