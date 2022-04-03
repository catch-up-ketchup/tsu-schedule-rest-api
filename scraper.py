import bs4
import requests

from typing import List
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from utils import get_type, get_text_safely, transform_date, transform_subject
from shelve_storage import shelve_storage


def create_daily_schedule_item(row: bs4.Tag) -> dict:
    """
    Данная функция формирует словарь с информацией о соответствующей паре

    :param row: объект строки таблицы
    :return: словарь с информацией
    """
    subject = get_text_safely(row, 'span.disc')
    auditorium = get_text_safely(row, 'span.aud > a').strip()
    time = get_text_safely(row, 'td.time').split('-')
    return {
        'subject': transform_subject(subject),
        'time': {
            'start': time[0],
            'end': time[1]
        },
        'auditorium': auditorium if len(auditorium) > 0 else 'Дистанционно',
        'teacher': get_text_safely(row, '.teac a'),
        'type': get_type(subject)
    }


def create_day(row: bs4.Tag) -> dict:
    """
    Данная функция формирует словарь с информацией о соответствующим дне занятий

    :param row: объект строки таблицы
    :return: словь с информацией
    """
    info = row.select_one('u').text
    return {
        'weekType': info[info.index('(') + 1:-1].split(' ')[0],
        'dayOfWeek': info[info.index('-') + 1: info.index('(')].strip(),
        'date': info[:info.index('-') - 1]
    }


def is_date(row: bs4.Tag) -> bool:
    """
    Данная функция определяет, является ли строка таблицы датой

    :param row: объект строки таблицы
    :return: True or False
    """
    columns = row.select('td')
    return bool(len(columns) % 2)


def get_schedule(group: str) -> List:
    """
    Данная функция формирует словарь с расписанием, она работает следующим образом:
        1) Отправляет запрос на сайт
        2) Если сайт работает, значит, он ответит с кодом 200, после чего пытаемся извлечь расписание
            3) Если переменная data пустая, значит, пользователь запросил расписание несуществующей группы
            4) Если же не пустая - формируем словарь с расписанием, возвращаем пользователю и заносим в хранилище
        5) Если сайт упал, значит, он ответит с другим кодом, тогда пытаемся извлечь расписание из хранилища,
           хранилище выбросит исключение, если расписания для такой группы не существует, поэтому обрабатываем его
        6) Если функция доходит до данного шага, значит, что-то всё-таки пошло не так, поэтому кидаем исключение

    :param group: номер группы
    :return: словарь с расписанием
    """
    try:
        connection_timeout = 2
        reading_timeout = 4.5

        response = requests.get(
            f'http://schedule.tsu.tula.ru/?group={group}',
            timeout=(connection_timeout, reading_timeout),
            headers={'User-Agent': generate_user_agent()}
        )
    except Exception:
        return shelve_storage.get_schedule(group)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
        
        data = soup.select_one('#results table.tt+.time+table.tt')
        data = data if data else soup.select_one('#results .time+table.tt')

        if data:
            rows = data.select('tr')[::-1]
            result, temp = [], []

            for row in rows:
                if is_date(row):
                    result.append({'day': create_day(row), 'dailySchedule': temp[::-1]})
                    temp = []
                else:
                    temp.append(create_daily_schedule_item(row))

            schedule = list(sorted(result, key=lambda item: transform_date(item['day']['date'])))
            shelve_storage.update_schedule(group, schedule)

            return schedule

    raise Exception('error')
