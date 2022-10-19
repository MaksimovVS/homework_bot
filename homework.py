import logging
import os
import time
from logging.config import fileConfig

import requests
from dotenv import load_dotenv
from requests import HTTPError
from telegram import Bot

from exceptions import TokenError

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
BEGINNING_TIME = 1
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
        homework_statuses.raise_for_status()

    logger.info("Worked out function get_api_answer")
    return homework_statuses.json()


def check_response(response):
    """Проверяет API на корректность."""
    if not isinstance(response, dict):
        logger.error("В функцию check_response пришёл не словарь")
        raise TypeError(
            "Unexpected response in check_response function, dict expected"
        )
    homeworks = response.get("homeworks")
    if homeworks is None:
        logger.error("В ответе API отсутствует ключ homeworks")
        raise KeyError("В ответе API отсутствует ключ homeworks")
    if not isinstance(homeworks, list):
        logger.error("Словарь homeworks содержит значения не в виде массива")
        raise TypeError("homeworks dictionary contains non-tuple values")
    logger.info("Worked out function check_response")
    return homeworks


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if not isinstance(homework, dict):
        raise TypeError(
            "Unexpected response in parse_status function, dict expected"
        )
    if len(homework) != 0:
        homework_name = homework.get("homework_name")
        if homework_name is None:
            message = "В homework отсутствует ключ homework_name"
            logger.error(message)
            raise KeyError(message)
        homework_status = homework.get("status")
        if homework_status is None:
            message = "В homework отсутствует ключ homework_status"
            logger.error(message)
            raise KeyError(message)
        verdict = HOMEWORK_STATUSES.get(homework_status)
        if verdict is None:
            message = "Ключ verdict отсутствует в ожидаемых ответах"
            logger.error(message)
            raise KeyError(message)

        logger.info("Worked out function parse_status")
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
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
    current_timestamp = BEGINNING_TIME

    sample_result = ""

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)[0]
            result = parse_status(homework)
            if result != sample_result:
                send_message(bot, result)
                sample_result = result

            current_timestamp = response.get("current_date")

        except HTTPError as error:
            logger.error(f"API not available {error}")
            send_message(bot, f"API Практикума недоступна {error}")

        except TypeError as error:
            send_message(bot, f"Неожиданный формат данных {error}")

        except KeyError as error:
            send_message(bot, f"Отсутствует ключ {error}")

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            send_message(bot, message)
        else:
            logger.debug("Цикл main успешен")
        finally:
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
