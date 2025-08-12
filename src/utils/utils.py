from typing import Dict, Any, Tuple, Optional, Union, List

import aiohttp
import wikipedia
from aiogram.types import BufferedInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from deep_translator import GoogleTranslator


def get_russian_name_from_latin(latin_name: str, lang: str) -> str:
    wikipedia.set_lang(lang)
    try:
        page = wikipedia.page(latin_name)
        return page.title
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Неоднозначность: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Не нашёл русского названия"


translation_cache = {}


def safe_translate(text: Union[str, List[str]], source_lang: str = 'auto', target_lang: str = 'ru') -> Union[
    str, List[str]]:
    if not text:
        return text
    if isinstance(text, str):
        if not text.strip():
            return text

        cache_key = (text.strip(), source_lang, target_lang)
        if cache_key in translation_cache:
            return translation_cache[cache_key]

        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text.strip())
            translation_cache[cache_key] = translated
            return translated
        except Exception as e:
            print(f"⚠️ Ошибка перевода '{text[:30]}...': {str(e)}")
            return text

    elif isinstance(text, list):
        translated_list = []
        for item in text:
            if isinstance(item, str):
                translated_item = safe_translate(item, source_lang, target_lang)
                translated_list.append(translated_item)
            else:
                print(f"⚠️ Пропущен элемент (не строка): {item}")
                translated_list.append(item)
        return translated_list

    else:
        print(f"⚠️ Неподдерживаемый тип: {type(text)}")
        return text

def list_to_string(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    elif isinstance(value, str):
        return value.strip()
    elif value is not None:
        return str(value)
    return ""

def format_plant_details(
        json_data: Dict[str, Any],
        language: str = 'ru'
) -> str:
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

        if language != 'ru':
            plant_names_list = [safe_translate(name, target_lang=language) for name in
                                common_names] if common_names else []
            plant_names = " / ".join(plant_names_list) if plant_names_list else safe_translate("Информация о растении",
                                                                                               target_lang=language)
            section_title_main = safe_translate("### 🌸 {name}", target_lang=language).replace("{name}", plant_names)
            section_title_latin = safe_translate("Латинское название", target_lang=language)
        else:
            plant_names = " / ".join(common_names) if common_names else "Информация о растении"
            section_title_main = f"### 🌸 {plant_names}"
            section_title_latin = "Латинское название"

        result = [f"<b>{section_title_main}</b>", f"<b>{section_title_latin}</b>: <i>{latin_name}</i>\n"]

        if taxonomy := details.get('taxonomy', {}):
            if isinstance(taxonomy, dict):
                tax_title = "#### 🌿 Таксономия"
                if language != 'ru':
                    tax_title = safe_translate(tax_title, target_lang=language)
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
                        title_trans = safe_translate(ru_title, target_lang=language) if language != 'ru' else ru_title
                        result.append(f"<b>{title_trans}</b>: {value}")
                result.append("")

        # Синонимы
        if synonyms := details.get('synonyms', []):
            if isinstance(synonyms, list):
                syn_title = "#### 🔍 Синонимы"
                if language != 'ru':
                    syn_title = safe_translate(syn_title, target_lang=language)
                result.append(f"<b>{syn_title}</b>")
                for synonym in synonyms:
                    trans_syn = safe_translate(synonym, target_lang=language) if language != 'ru' else synonym
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
                            freq_key = safe_translate(freq_key, target_lang=language)
                        watering_text.append(f"<b>{freq_key}</b>: {freq}")
                    except (TypeError, ValueError):
                        pass

        if best_watering := details.get('best_watering'):
            label = "Рекомендации"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            best_watering = safe_translate(best_watering, target_lang=language)
            watering_text.append(f"<b>{label}</b>: {best_watering}")

        if watering_text:
            section = "💧 Полив"
            if language != 'ru':
                section = safe_translate(section, target_lang=language)
            care_sections.append(f"<b>{section}</b>\n" + "\n".join(watering_text))

        if light := details.get('best_light_condition'):
            label = "☀️ Освещение"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            light = safe_translate(light, target_lang=language)
            care_sections.append(f"<b>{label}</b>\n— {light}")

        if soil := details.get('best_soil_type'):
            label = "🌱 Почва"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            soil = safe_translate(soil, target_lang=language)
            care_sections.append(f"<b>{label}</b>\n— {soil}")

        if care_sections:
            care_title = "#### 💧 Уход за растением"
            if language != 'ru':
                care_title = safe_translate(care_title, target_lang=language)
            result.append(f"<b>{care_title}</b>")
            result.extend(care_sections)
            result.append("")

        # Применение
        usage_sections = []

        if toxicity := details.get('toxicity'):
            label = "⚠️ Токсичность"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            toxicity = safe_translate(toxicity, target_lang=language)
            usage_sections.append(f"<b>{label}</b>\n— {toxicity}")

        if uses := details.get('common_uses'):
            label = "🌼 Применение"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            uses = safe_translate(uses, target_lang=language)
            usage_sections.append(f"<b>{label}</b>\n— {uses}")

        if culture := details.get('cultural_significance'):
            label = "🎎 Культурное значение"
            if language != 'ru':
                label = safe_translate(label, target_lang=language)
            culture = safe_translate(culture, target_lang=language)
            usage_sections.append(f"<b>{label}</b>\n— {culture}")

        if usage_sections:
            title = "#### 🌼 Применение и особенности"
            if language != 'ru':
                title = safe_translate(title, target_lang=language)
            result.append(f"<b>{title}</b>")
            result.extend(usage_sections)
            result.append("")

        # Дополнительно
        extra_info = []

        edible = details.get('edible_parts')
        edible_label = "Съедобные части"
        if edible:
            edible = safe_translate(edible, target_lang=language)
            edible_label = safe_translate(edible_label, target_lang=language)
            extra_info.append(f"<b>{edible_label}</b>: {edible}")
        else:
            value = "Не указаны"
            if language != 'ru':
                edible_label = safe_translate(edible_label, target_lang=language)
            value = safe_translate(value, target_lang=language)
            extra_info.append(f"<b>{edible_label}</b>: {value}")

        propagation = details.get('propagation_methods')
        prop_label = "Способы размножения"
        if propagation:
            if language != 'ru':
                prop_label = safe_translate(prop_label, target_lang=language)
            propagation = safe_translate(propagation, target_lang=language)
            extra_info.append(f"<b>{prop_label}</b>: {propagation}")
        else:
            value = "Данные отсутствуют"
            if language != 'ru':
                prop_label = safe_translate(prop_label, target_lang=language)
            value = safe_translate(value, target_lang=language)
            extra_info.append(f"<b>{prop_label}</b>: {value}")

        if extra_info:
            title = "#### ❓ Дополнительно"
            if language != 'ru':
                title = safe_translate(title, target_lang=language)
            result.append(f"<b>{title}</b>")
            result.extend(extra_info)
            result.append("")

        return "\n".join(result)

    except Exception as e:
        error_msg = f"❌ Критическая ошибка форматирования данных: {str(e)}"
        return safe_translate(error_msg, target_lang=language) if language != 'ru' else error_msg


async def download_similar_images(
        similar_images: List[Dict[str, Any]]
) -> List[Tuple[bytes, Dict[str, Any]]]:
    results = []
    async with aiohttp.ClientSession() as session:
        for img in similar_images:
            image_url = img.get("url_small") or img.get("url")
            if not image_url:
                print(f"[WARNING] URL изображения не найден в данных: {img}")
                continue
            if isinstance(image_url, list):
                print(f"[WARNING] URL изображения — список, используем первый элемент: {image_url}")
                image_url = image_url[0] if len(image_url) > 0 else None
            elif not isinstance(image_url, str):
                print(f"[WARNING] Некорректный тип URL изображения (не строка): {type(image_url)}")
                continue
            if not image_url:
                continue
            print(image_url)
            image_url = image_url.strip()
            try:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        metadata = {
                            "similarity": img["similarity"],
                            "license_name": img.get("license_name"),
                            "license_url": img.get("license_url", "").strip() if img.get("license_url") else None,
                            "citation": img.get("citation"),
                            "source_url": image_url
                        }
                        results.append((image_data, metadata))
                        print(f"[INFO] Успешно загружено изображение: {image_url}")
                    else:
                        print(f"[ERROR] Ошибка загрузки изображения {image_url}: статус {response.status}")
            except Exception as e:
                print(f"[ERROR] Исключение при загрузке изображения {image_url}: {str(e)}")

    return results  # ← не забудь вернуть результат!


def build_similar_images_media_group(
        downloaded_images: List[Tuple[bytes, Dict[str, Any]]],
        plant_name: str,
        common_name: Optional[str] = None
) -> Optional[MediaGroupBuilder]:
    if not downloaded_images:
        return None
    media_group = MediaGroupBuilder(caption="")
    plant_info = f"📸 <b>Похожие изображения:</b> {plant_name}"
    if common_name:
        plant_info += f" (<i>{common_name}</i>)"
    for i, (image_data, metadata) in enumerate(downloaded_images):
        similarity = f"Сходство: {metadata['similarity'] * 100:.1f}%"
        license_info = ""
        if metadata.get("license_name"):
            license_info = f"\n\n<b>Лицензия:</b> {metadata['license_name']}"
            if metadata.get("citation"):
                license_info += f" (Автор: {metadata['citation']})"
            if metadata.get("license_url"):
                license_info += f"\n{metadata['license_url']}"
        if i == 0:
            caption = f"{plant_info}\n\n{similarity}{license_info}"
            media_group.add_photo(
                media=BufferedInputFile(image_data, filename=f"plant_{i}.jpg"),
                caption=caption,
                parse_mode="HTML"
            )
        else:
            caption = f"{similarity}{license_info}"
            media_group.add_photo(
                media=BufferedInputFile(image_data, filename=f"plant_{i}.jpg"),
                caption=caption,
                parse_mode="HTML"
            )
    return media_group


def parse_plant_health_response(
        json_data: Dict[str, Any],
        language: str = 'ru',
        ai_treatment_response: Optional[str] = None
) -> str:
    try:
        result_data = json_data.get('result', {})
        is_plant = result_data.get('is_plant', {}).get('binary', False)
        plant_probability = result_data.get('is_plant', {}).get('probability', 0)

        if not is_plant:
            msg = f"Анализ показывает, что предоставленное изображение, скорее всего, НЕ содержит растение (вероятность: {1 - plant_probability:.2%})."
            return safe_translate(msg, target_lang=language) if language != 'ru' else msg

        is_healthy = result_data.get('is_healthy', {}).get('binary', True)
        health_probability = result_data.get('is_healthy', {}).get('probability', 1.0)

        result_lines = []

        title = "### 🌿 Состояние здоровья растения"
        if language != 'ru':
            title = safe_translate(title, target_lang=language)
        result_lines.append(f"<b>{title}</b>\n")

        if is_healthy:
            health_msg = f"Растение выглядит здоровым (вероятность здоровья: {health_probability:.2%})."
            if language != 'ru':
                health_msg = safe_translate(health_msg, target_lang=language)
            result_lines.append(f"✅ <b>{health_msg}</b>\n")
            return "\n".join(result_lines)
        else:
            health_msg = f"Растение, вероятно, имеет проблемы со здоровьем (вероятность здоровья: всего {health_probability:.2%})."
            if language != 'ru':
                health_msg = safe_translate(health_msg, target_lang=language)
            result_lines.append(f"⚠️ <b>{health_msg}</b>\n")

        disease_section = "#### 🩺 Возможные проблемы"
        if language != 'ru':
            disease_section = safe_translate(disease_section, target_lang=language)
        result_lines.append(f"<b>{disease_section}</b>")

        suggestions = result_data.get('disease', {}).get('suggestions', [])
        if not suggestions:
            no_issues_msg = "Не удалось определить конкретные проблемы. Пожалуйста, проверьте изображение и повторите запрос."
            if language != 'ru':
                no_issues_msg = safe_translate(no_issues_msg, target_lang=language)
            result_lines.append(f"— {no_issues_msg}")
        else:
            for i, suggestion in enumerate(suggestions[:3], 1):
                name = suggestion.get('name', 'Неизвестная проблема')
                probability = suggestion.get('probability', 0)

                translated_name = safe_translate(name, target_lang=language) if language != 'ru' else name
                problem_line = f"{i}. {translated_name.capitalize()} — <b>{probability:.2%}</b>"
                result_lines.append(f"— {problem_line}")

        question_data = result_data.get('disease', {}).get('question', {})
        if question_data:
            question_text = question_data.get('text', '')
            if question_text:
                diag_section = "#### ❓ Диагностический вопрос"
                if language != 'ru':
                    diag_section = safe_translate(diag_section, target_lang=language)
                result_lines.append(f"\n<b>{diag_section}</b>")

                translated_question = safe_translate(question_text,
                                                     target_lang=language) if language != 'ru' else question_text
                result_lines.append(f"— {translated_question}")

                options = question_data.get('options', {})
                yes_opt = options.get('yes', {})
                no_opt = options.get('no', {})
                if yes_opt and no_opt:
                    yes_index = yes_opt.get('suggestion_index', 0)
                    no_index = no_opt.get('suggestion_index', 0)

                    yes_problem = suggestions[yes_index]['name'] if yes_index < len(suggestions) else "проблема"
                    no_problem = suggestions[no_index]['name'] if no_index < len(suggestions) else "проблема"

                    yes_problem_trans = safe_translate(yes_problem,
                                                       target_lang=language) if language != 'ru' else yes_problem
                    no_problem_trans = safe_translate(no_problem,
                                                      target_lang=language) if language != 'ru' else no_problem

                    yes_label = "Да" if language == 'ru' else safe_translate("Yes", target_lang=language)
                    no_label = "Нет" if language == 'ru' else safe_translate("No", target_lang=language)

                    result_lines.append(f"   • {yes_label}: <i>{yes_problem_trans}</i>")
                    result_lines.append(f"   • {no_label}: <i>{no_problem_trans}</i>")

        if ai_treatment_response:
            treatment_section = "#### 💊 Рекомендации по лечению"
            if language != 'ru':
                treatment_section = safe_translate(treatment_section, target_lang=language)
            result_lines.append(f"\n<b>{treatment_section}</b>")
            result_lines.append(ai_treatment_response.strip())

        license_note = "ℹ️ Примечание: Изображения для сравнения лицензированы под CC BY-NC-SA 4.0 (разрешено некоммерческое использование с указанием авторства и обязательным распространением производных работ на тех же условиях)."
        if language != 'ru':
            license_note = safe_translate(license_note, target_lang=language)
        result_lines.append(f"\n{license_note}")

        return "\n".join(result_lines)

    except Exception as e:
        error_msg = f"❌ Критическая ошибка форматирования данных: {str(e)}"
        print(error_msg)
        raise Exception(safe_translate(error_msg, target_lang=language) if language != 'ru' else error_msg) from e


def split_text(text: str, max_length: int = 4096) -> list[str]:
    if len(text) <= max_length:
        return [text]

    parts = []
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(text[:split_index])
        text = text[split_index:].lstrip()
    parts.append(text)
    return parts
