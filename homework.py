import os
import sys
from pprint import pprint

import requests
import time
import logging

from dotenv import load_dotenv
from logging.config import fileConfig


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)






def send_message(bot, message):
    pass


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if homework_statuses.status_code != 200:
        raise TypeError('ПЕРЕПИШИ ОШИБКУ, тут говно со статусом') # ToDo Подумай как исправить ошибку
    b = homework_statuses.json()

    return homework_statuses.json()


def check_response(response):
    if isinstance(response, dict):
        homeworks = response.get('homeworks')
        if len(homeworks) != 0:
            return homeworks[0]
        return homeworks
    raise TypeError('В функцию check_response был передан не словарь')


def parse_status(homework):
    if len(homework) != 0:
        if isinstance(homework, dict):
            homework_name = homework['homework_name']

            homework_status = homework.get('status')

            # ...

            verdict = HOMEWORK_STATUSES.get(homework_status)

            # ...

            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        else:
            raise KeyError('Тут какое-то говно - поправь') # ToDo подумай как поменять ошибку
    return 'За выбранный отрезок времени нет проверенных работ'


def check_tokens():
    '''Проверяет доступность переменных окружения.'''
    if not PRACTICUM_TOKEN:
        return False
    if not TELEGRAM_TOKEN:
        return False
    if not TELEGRAM_CHAT_ID:
        return False
    return True

def main():
    """Основная логика работы бота."""

    # ...

    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1 # int(time.time())

    # ...

    # while True:
        # try:
            # response = ...

            # ...

            # current_timestamp = ...
            # time.sleep(RETRY_TIME)

        # except Exception as error:
            # message = f'Сбой в работе программы: {error}'
            # ...
            # time.sleep(RETRY_TIME)
        # else:
            # ...
    response = get_api_answer(current_timestamp)
    print(parse_status(check_response(response)))



if __name__ == '__main__':
    main()
