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

RETRY_TIME = 60
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
    logger.info("Произошел запрос к API")

    if homework_statuses.status_code != 200:
        homework_statuses.raise_for_status()

    logger.info("Worked out function get_api_answer")
    try:
        return homework_statuses.json()
    except Exception:
        message = "Ответвет API не json"
        logger.error(message)


def check_response(response):
    """Проверяет API на корректность."""
    if not isinstance(response, dict):
        logger.error("В функцию check_response пришёл не словарь")
        raise TypeError(
            "Unexpected response in check_response function, dict expected"
        )
    homeworks = check_key_in_dict(response, "homeworks")
    if not isinstance(homeworks, list):
        logger.error("Словарь homeworks содержит значения не в виде массива")
        raise TypeError("homeworks dictionary contains non-tuple values")
    logger.info("Worked out function check_response")
    return homeworks


def check_key_in_dict(dictionary, key):
    """Райзит KeyError и пишет в бот если в словаре нет нужного ключа."""
    value = dictionary.get(key)
    if value is not None:
        return value
    message = f"В ответе API отсутствует ключ {key}"
    logger.error(message)
    raise KeyError(message)


def parse_status(homework):
    """Извлекает информацию о конкретной домашней работе."""
    if not isinstance(homework, dict):
        raise TypeError(
            "Unexpected response in parse_status function, dict expected"
        )
    homework_name = check_key_in_dict(homework, "homework_name")
    homework_status = check_key_in_dict(homework, "status")
    verdict = check_key_in_dict(HOMEWORK_STATUSES, homework_status)

    logger.info("Worked out function parse_status")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.error(TokenError)
        raise TokenError()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = BEGINNING_TIME

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                result = parse_status(homeworks[0])
                send_message(bot, result)
            current_timestamp = response.get("current_date")

        except HTTPError as error:
            logger.error(f"API not available {error}")
            send_message(bot, f"API Практикума недоступна {error}")

        except TypeError as error:
            message = f"Неожиданный формат данных {error}"
            logger.error(message)
            send_message(bot, message)

        except KeyError as error:
            message = f"Отсутствует ключ {error}"
            logger.error(message)
            send_message(bot, message)

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message)
            send_message(bot, message)
        else:
            logger.debug("Цикл main успешен")
        finally:
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
