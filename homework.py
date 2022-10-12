import os
from pprint import pprint

import requests
import time

from dotenv import load_dotenv


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


def send_message(bot, message):
    pass


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return homework_statuses.json()


def check_response(response):

    homeworks = response.get('homeworks')
    return homeworks


def parse_status(homework):
    # homework_name = ...
    # homework_status = ...

    # ...

    # verdict = ...

    # ...

    # return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    pass

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
    # current_timestamp = int(time.time())

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
    response = get_api_answer(1)
    pprint(check_response(response))


if __name__ == '__main__':
    main()
