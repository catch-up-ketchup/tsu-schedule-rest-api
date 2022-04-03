from typing import List, Any, Callable
from urllib.parse import unquote_to_bytes, quote

import datetime
import bs4


def transform_date(string: str) -> datetime:
    """
    Данная функция преобразует дату к другому виду,
    который python умеет сравнивать (используется для сортировки)

    :param string: дата вида 25.03.22
    :return: дата вида 2022.03.25
    """
    lst = string.split('.')[::-1]
    lst[0] = f'20{lst[0]}'
    return '.'.join(lst)


def get_text_safely(parent_tag: bs4.Tag, selector: str) -> str:
    """
    Данная функция безопасно извелкает текст из дочернего тега
    Если дочернего тега не существует - при обращении к его атрибуту .text
    мы получим исключение, а здесь мы его обрабатываем

    :param parent_tag: объект родительского тега
    :param selector: селектор дочернего тега
    :return: текст тега или пустая строка
    """
    try:
        return parent_tag.select_one(selector).text
    except AttributeError:
        return ''


def get_item(lst: List, callback: Callable[[Any], bool]) -> Any:
    """
    Данная функция возвращает элемент списка, который удовлетворяет
    переданному коллбэку

    :param lst: список
    :param callback: условие
    :return: элемент, который удовлетворяет условию
    """
    for item in lst:
        if callback(item):
            return item
    return None


def get_subgroup(subject: str) -> str:
    """
    Данная функция достаёт подгруппы из строк следующего вида:
        'Иностранный язык (Практические занятия для ИЯ (фр))' -> 'фр'
        'Объемно-пространственная композиция (Практические занятия)(2 пг)' -> '2'
        'Инженерная геодезия и основы топографии (Лабораторные работы)(2 пг)' -> '2'
        'Практикум на электронных вычислительных машинах (Лабораторные работы)(2 подгруппа)' -> '2'
        'Инженерная геодезия и основы топографии (Лабораторные работы)(2 подгруппа)' -> '2'
        'Оценка бизнеса (Практические занятия)(1пг)' -> '1'

    :param subject: полное название предмета, что в скобках
    :return: подгруппа (если она есть)
    """

    if 'Иностранный язык' in subject:
        return subject[subject.rfind('(') + 1:subject.find(')')]

    key_words = ['подгруппа', 'пг']
    indexes = [subject.find(key_word) for key_word in key_words]
    index = get_item(indexes, lambda item: item != -1)
    temp = subject[:index]

    return subject[temp.rfind('(') + 1] if index else ''


def get_type(subject: str) -> dict:
    """
    Данная функция предназначена для определения типа пары.
    Ключи результирующего словаря:
        'ru': Полное название типа пары на русском языке (отображается на сайте)
        'en': Сокращённое название типа пары на английском (на фронте используется в качетсве модификатора класса)
        'subgroup': Подгруппа, если таковая имеется

    :param subject: название предмета и всё, что в скобках
    :return: тип предмета в виде словаря
    """
    result = {
        'ru': '',
        'en': '',
        'subgroup': ''
    }

    if 'Лабораторные работы' in subject:
        result['ru'] = 'Лабораторные работы'
        result['en'] = 'laboratory-work'
    elif 'Практические занятия' in subject:
        result['ru'] = 'Практические занятия'
        result['en'] = 'practice'
    elif 'Практ. клинические' in subject:
        result['ru'] = 'Практ. клинические'
        result['en'] = 'practice'
    elif 'Лекционные занятия' in subject:
        result['ru'] = 'Лекционные занятия'
        result['en'] = 'lecture'
    else:
        result['ru'] = 'Другое'
        result['en'] = 'another'

    result['subgroup'] = get_subgroup(subject)
    return result


def transform_subject(subject: str) -> str:
    """
    Данная функция возвращает только название предмета, например:
        'Иностранный язык (Практические занятия для ИЯ (фр))' -> 'Иностранный язык'

    :param subject: название предмета и всё, что в скобках
    :return: название предмета
    """
    index = subject.find('(')
    subject_name = subject[:index] if index != -1 else subject
    return subject_name.strip()


def quote_text(text, reverse=False):
    """
    Данная функция предназнчена для шифровки / расшифровки текста, например:
        'ПБ' -> '%D0%9F%D0%91'
        '%D0%9F%D0%91', True -> 'ПБ'

    :param text: обычный / зашифрованный текст
    :param reverse: True or False
    :return: зашифрованный / обычный текст
    """
    if reverse:
        return unquote_to_bytes(text).decode('utf-8')
    return quote(text, safe='_-=/()&?:;%"')
