from typing import Dict, Any

import requests
from deep_translator import GoogleTranslator

from src.utils.find_name_flower import get_russian_name_from_latin


def handle_photo(photo,
                 ai_token: str,
                 language: str = 'ru'
                 ) -> (str, str | None):
    try:
        data = {
            'images': [photo],
        }
        params = {
            'language': 'ru',
            'details': 'common_names,description,taxonomy,synonyms,edible_parts,propagation_methods,watering,best_watering,best_light_condition,best_soil_type,common_uses,toxicity,cultural_significance'
        }
        headers = {'api-key': ai_token}
        response = requests.post(f"https://api.plant.id/v3/identification",
                                 headers=headers, json=data, params=params)
        response.raise_for_status()
        response_json = response.json()
        print(response_json)
        if 'result' in response_json and 'classification' in response_json['result'] and 'suggestions' in \
                response_json['result']['classification']:
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
                details = top_suggestion.get('details', {})
                description = details.get('description', '')
                edible_parts = details.get('edible_parts', [])
                toxicity = details.get('toxicity', '')
                common_names = details.get('common_names', [])
                lines = [
                    f"Вероятнее всего это: {common_names[0] if common_names else get_russian_name_from_latin(plant_name, language)}",
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


def get_details(
        access_token: str,
        ai_token: str,
        language: str = 'ru'
) -> str:
    try:
        headers = {'api-key': ai_token}
        print(language)
        params = {
            'language': language,
            'details': 'common_names,description,taxonomy,synonyms,edible_parts,propagation_methods,watering,best_watering,best_light_condition,best_soil_type,common_uses,toxicity,cultural_significance'
        }
        response = requests.get(f"https://api.plant.id/v3/identification/{access_token}", headers=headers,
                                params=params)
        response.raise_for_status()
        response_json = response.json()
        return format_plant_details(response_json, language)
    except requests.exceptions.RequestException as e:
        print(e)
        raise Exception(f"ошибка запроса к нейронке:\n{e}")
    except Exception as e:
        print(e)
        raise Exception(f"Неожиданная ошибка:\n{e}")


def format_plant_details(
        json_data: Dict[str, Any],
        language: str = 'ru'
) -> str:
    translation_cache = {}

    def safe_translate(text: str, source_lang: str = 'auto') -> str:
        if not text.strip():
            print("1")
            return text
        if text in translation_cache:
            print("2")
            return translation_cache[text]

        try:
            translator = GoogleTranslator(source=source_lang, target=language)
            translated = translator.translate(text)
            translation_cache[text] = translated
            print(translated)
            return translated
        except Exception as e:
            print(f"⚠️ Ошибка перевода '{text[:30]}...': {str(e)}")
            return text

    try:
        result_data = json_data.get('result', {})
        classification = result_data.get('classification', {})
        suggestions = classification.get('suggestions', [])
        plant = suggestions[0] if suggestions else {}
        details = plant.get('details', {}) or {}
        if not isinstance(details, dict):
            details = {}

        latin_name = plant.get('name', 'Неизвестное растение')
        common_names = details.get('common_names', [])
        if isinstance(common_names, str):
            common_names = [common_names]
        elif not isinstance(common_names, list):
            common_names = []

        # Переводим все текстовые константы и данные
        if language != 'ru':
            plant_names_list = [safe_translate(name) for name in common_names] if common_names else []
            plant_names = " / ".join(plant_names_list) if plant_names_list else safe_translate("Информация о растении")
            latin_name = latin_name  # Латинское название не переводим
            section_title_main = safe_translate("### 🌸 {name}").replace("{name}", plant_names)
            section_title_latin = safe_translate("Латинское название")
        else:
            plant_names = " / ".join(common_names) if common_names else "Информация о растении"
            section_title_main = f"### 🌸 {plant_names}"
            section_title_latin = "Латинское название"

        result = [f"<b>{section_title_main}</b>", f"<b>{section_title_latin}</b>: <i>{latin_name}</i>\n"]

        # Таксономия
        if taxonomy := details.get('taxonomy', {}):
            if isinstance(taxonomy, dict):
                tax_title = "#### 🌿 Таксономия"
                if language != 'ru':
                    tax_title = safe_translate(tax_title)
                result.append(f"<b>{tax_title}</b>")
                tax_map = {
                    'kingdom': 'Царство',
                    'phylum': 'Отдел',
                    'class': 'Класс',
                    'order': 'Порядок',
                    'family': 'Семейство',
                    'genus': 'Род'
                }
                for key, ru_title in tax_map.items():
                    if value := taxonomy.get(key):
                        title_trans = safe_translate(ru_title) if language != 'ru' else ru_title
                        result.append(f"<b>{title_trans}</b>: {value}")
                result.append("")

        # Синонимы
        if synonyms := details.get('synonyms', []):
            if isinstance(synonyms, list):
                syn_title = "#### 🔍 Синонимы"
                if language != 'ru':
                    syn_title = safe_translate(syn_title)
                result.append(f"<b>{syn_title}</b>")
                for synonym in synonyms:
                    trans_syn = safe_translate(synonym) if language != 'ru' else synonym
                    result.append(f"<i>{trans_syn}</i>")
                result.append("")

        # Уход
        care_sections = []
        watering_text = []

        if watering := details.get('watering', {}):
            if isinstance(watering, dict):
                min_val = watering.get('min')
                max_val = watering.get('max')
                if min_val is not None and max_val is not None:
                    try:
                        min_val = float(min_val)
                        max_val = float(max_val)
                        freq_key = "Частота"
                        if min_val == max_val:
                            freq = f"{int(min_val)} раз{'а' if 2 <= min_val <= 4 else ''}"
                        else:
                            freq = f"{int(min_val)}–{int(max_val)} раз в неделю"
                        if language != 'ru':
                            freq_key = safe_translate(freq_key)
                        watering_text.append(f"<b>{freq_key}</b>: {freq}")
                    except (TypeError, ValueError):
                        pass

        if best_watering := details.get('best_watering'):
            label = "Рекомендации"
            if language != 'ru':
                label = safe_translate(label)
            best_watering = safe_translate(best_watering)
            watering_text.append(f"<b>{label}</b>: {best_watering}")

        if watering_text:
            section = "💧 Полив"
            if language != 'ru':
                section = safe_translate(section)
            care_sections.append(f"<b>{section}</b>\n" + "\n".join(watering_text))

        if light := details.get('best_light_condition'):
            label = "☀️ Освещение"
            if language != 'ru':
                label = safe_translate(label)
            light = safe_translate(light)
            care_sections.append(f"<b>{label}</b>\n— {light}")

        if soil := details.get('best_soil_type'):
            label = "🌱 Почва"
            if language != 'ru':
                label = safe_translate(label)
            soil = safe_translate(soil)
            care_sections.append(f"<b>{label}</b>\n— {soil}")

        if care_sections:
            care_title = "#### 💧 Уход за растением"
            if language != 'ru':
                care_title = safe_translate(care_title)
            result.append(f"<b>{care_title}</b>")
            result.extend(care_sections)
            result.append("")

        # Применение и особенности
        usage_sections = []

        if toxicity := details.get('toxicity'):
            label = "⚠️ Токсичность"
            if language != 'ru':
                label = safe_translate(label)
            toxicity = safe_translate(toxicity)
            usage_sections.append(f"<b>{label}</b>\n— {toxicity}")

        if uses := details.get('common_uses'):
            label = "🌼 Применение"
            if language != 'ru':
                label = safe_translate(label)
            uses = safe_translate(uses)
            usage_sections.append(f"<b>{label}</b>\n— {uses}")

        if culture := details.get('cultural_significance'):
            label = "🎎 Культурное значение"
            if language != 'ru':
                label = safe_translate(label)
            culture = safe_translate(culture)
            usage_sections.append(f"<b>{label}</b>\n— {culture}")

        if usage_sections:
            title = "#### 🌼 Применение и особенности"
            if language != 'ru':
                title = safe_translate(title)
            result.append(f"<b>{title}</b>")
            result.extend(usage_sections)
            result.append("")

        # Дополнительно
        extra_info = []

        edible = details.get('edible_parts')
        edible_label = "Съедобные части"
        if edible:
            if language != 'ru':
                edible = safe_translate(edible)
            edible_label = safe_translate(edible_label)
            extra_info.append(f"<b>{edible_label}</b>: {edible}")
        else:
            value = "Не указаны"
            if language != 'ru':
                edible_label = safe_translate(edible_label)
            value = safe_translate(value)
            extra_info.append(f"<b>{edible_label}</b>: {value}")

        propagation = details.get('propagation_methods')
        prop_label = "Способы размножения"
        if propagation:
            if language != 'ru':
                prop_label = safe_translate(prop_label)
            propagation = safe_translate(propagation)
            extra_info.append(f"<b>{prop_label}</b>: {propagation}")
        else:
            value = "Данные отсутствуют"
            if language != 'ru':
                prop_label = safe_translate(prop_label)
            value = safe_translate(value)
            extra_info.append(f"<b>{prop_label}</b>: {value}")

        if extra_info:
            title = "#### ❓ Дополнительно"
            if language != 'ru':
                title = safe_translate(title)
            result.append(f"<b>{title}</b>")
            result.extend(extra_info)
            result.append("")
        return "\n".join(result)

    except Exception as e:
        error_msg = f"❌ Критическая ошибка форматирования данных: {str(e)}"
        return safe_translate(error_msg) if language != 'ru' else error_msg
