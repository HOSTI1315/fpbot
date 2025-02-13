import re
from functools import lru_cache

# Предкомпиляция регулярных выражений
TIME_REGEX = re.compile(r"(\d{1,2}:\d{2}:\d{2})")
PRICE_REGEX = re.compile(r"(\d+)\s*(руб|р|рублей|₽)", re.IGNORECASE)

@lru_cache(maxsize=128)
def convert_date_time(date_time_str):
    """
    Преобразует строку с датой и временем в формате "21 января, 21:44:53"
    в формат "21.01 21:44:53".
    """
    match = re.search(r"(\d{1,2})\s+([а-я]+),\s+(\d{1,2}:\d{2}:\d{2})", date_time_str, re.IGNORECASE)
    if not match:
        return None
    day, month, time = match.groups()
    month_number = MONTHS.get(month.lower())
    if not month_number:
        return None
    return f"{day}.{month_number} {time}"

@lru_cache(maxsize=128)
def extract_time(date_time_str):
    """
    Извлекает время из строки в формате "21 января, 21:44:53".
    """
    match = TIME_REGEX.search(date_time_str)
    return match.group(1) if match else None

MONTHS = {
    "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
    "мая": "05", "июня": "06", "июля": "07", "августа": "08",
    "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
}

def generate_variants(base_name, base_variants, prefixes, prefix_type):
    """
    Генерирует все возможные варианты для фрукта/юнита с учетом префиксов.

    :param base_name: Базовое название фрукта/юнита
    :param base_variants: Базовые варианты названия
    :param prefixes: Словарь префиксов и их альтернатив
    :param prefix_type: Тип префикса (например, 'perm' или 'shiny')
    :return: Список всех возможных вариантов
    """
    result = []
    for variant in base_variants:
        result.append(variant)
        if prefix_type in prefixes:
            for prefix in prefixes[prefix_type]:
                prefixed_variant = f"{prefix} {variant}"
                result.append(prefixed_variant)
    return result