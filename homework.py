import logging
import os
import time
from logging.config import fileConfig
from pprint import pprint

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import TokenError

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


fileConfig("logging_config.ini")
logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправка сообщения в Телеграм."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.info("Telegram message sent")


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}

    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)

    if homework_statuses.status_code != 200:
        logger.error("API not available")
        homework_statuses.raise_for_status()

    logger.info("Worked out function get_api_answer")
    return homework_statuses.json()


def check_response(response):
    """Проверяет API на корректность."""
    if isinstance(response, dict):
        homeworks = response.get("homeworks")
        if len(homeworks) != 0:
            logger.info("Worked out function check_response")
            return homeworks[0]
        logger.info("Worked out function check_response (no homework)")
        return homeworks
    raise TypeError("В функцию check_response был передан не словарь")


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if len(homework) != 0:
        if isinstance(homework, dict):
            homework_name = homework.get("homework_name")
            homework_status = homework.get("status")
            verdict = HOMEWORK_STATUSES.get(homework_status)

            logger.info("Worked out function parse_status")
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        else:
            raise KeyError(
                "Тут какое-то говно - поправь"
            )  # ToDo подумай как поменять ошибку
    logger.info("Worked out function parse_status (no homework)")
    return "За выбранный отрезок времени нет проверенных работ"


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN:
        logger.critical("Invalid or unavailable token PRACTICUM_TOKEN")
        return False
    if not TELEGRAM_TOKEN:
        logger.critical("Invalid or unavailable token TELEGRAM_TOKEN")
        return False
    if not TELEGRAM_CHAT_ID:
        logger.critical("Invalid or unavailable token TELEGRAM_CHAT_ID")
        return False
    logger.info("Worked out function check_tokens")
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise TokenError()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1  # int(time.time())

    response = get_api_answer(current_timestamp)
    sample_result = parse_status(check_response(response))

    while True:
        try:
            response = get_api_answer(current_timestamp)
            result = parse_status(check_response(response))
            if result != sample_result:
                send_message(result)
                sample_result = result

            # current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            send_message(message)
            time.sleep(RETRY_TIME)
        # else:
        # ...


if __name__ == "__main__":
    main()
