from typing import List, Dict, Any, Tuple, Optional

import aiohttp
import wikipedia
from aiogram.types import BufferedInputFile  # Правильный импорт вместо InputFile
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


def format_plant_details(
        json_data: Dict[str, Any],
        language: str = 'ru'
) -> str:
    translation_cache = {}

    def safe_translate(text: str, source_lang: str = 'auto') -> str:
        if not text.strip():
            return text
        if text in translation_cache:
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
        if language != 'ru':
            plant_names_list = [safe_translate(name) for name in common_names] if common_names else []
            plant_names = " / ".join(plant_names_list) if plant_names_list else safe_translate("Информация о растении")
            latin_name = latin_name
            section_title_main = safe_translate("### 🌸 {name}").replace("{name}", plant_names)
            section_title_latin = safe_translate("Латинское название")
        else:
            plant_names = " / ".join(common_names) if common_names else "Информация о растении"
            section_title_main = f"### 🌸 {plant_names}"
            section_title_latin = "Латинское название"

        result = [f"<b>{section_title_main}</b>", f"<b>{section_title_latin}</b>: <i>{latin_name}</i>\n"]

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


async def download_similar_images(
        similar_images: List[Dict[str, Any]]
) -> List[Tuple[bytes, Dict[str, Any]]]:
    results = []
    async with aiohttp.ClientSession() as session:
        for img in similar_images:
            image_url = img.get("url_small", img.get("url"))
            if not image_url:
                print(f"[WARNING] URL изображения не найден в данных: {img}")
                continue
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

    return results


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
            # ИСПРАВЛЕНИЕ: используем BufferedInputFile вместо InputFile
            media_group.add_photo(
                media=BufferedInputFile(image_data, filename=f"plant_{i}.jpg"),
                caption=caption,
                parse_mode="HTML"
            )
        else:
            caption = f"{similarity}{license_info}"
            # ИСПРАВЛЕНИЕ: используем BufferedInputFile вместо InputFile
            media_group.add_photo(
                media=BufferedInputFile(image_data, filename=f"plant_{i}.jpg"),
                caption=caption,
                parse_mode="HTML"
            )

    return media_group
