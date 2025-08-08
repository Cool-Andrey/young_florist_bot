import wikipedia

def get_russian_name_from_latin(latin_name : str, lang : str) -> str:
    wikipedia.set_lang(lang)
    try:
        page = wikipedia.page(latin_name)
        return page.title
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Неоднозначность: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Не нашёл русского названия"
