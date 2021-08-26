import os
import time
import requests
import telegram
import logging
from http import HTTPStatus
from dotenv import load_dotenv


load_dotenv()


class TGBotException(Exception):
    pass


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise TGBotException('Сообщение не содержит обязательных полей')
    homework_statuses = homework.get('status')
    if homework_statuses is None:
        raise TGBotException('Сообщение не содержит обязательных полей')
    if homework_statuses == 'reviewing':
        verdict = 'Работа взята в ревью.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    if homework_statuses == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    if homework_statuses == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        raise TGBotException('Значение поля заполнено неверно')


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException('Ошибка при работе с API')
    answer = homework_statuses.json()
    if homework_statuses.status_code != HTTPStatus.OK:
        raise requests.exceptions.RequestException(
            'Ошибка при работе с сервером')
    else:
        return answer


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            logging.debug('Отслеживание статуса запущено')
            send_message(
                parse_homework_status(
                    get_homeworks(current_timestamp)['homeworks'][0]
                )
            )
            logging.info('Бот отправил сообщение')
            time.sleep(15 * 60)

        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.error(error_message)
            bot.send_message(chat_id=CHAT_ID, text=error_message)
            time.sleep(15)


if __name__ == '__main__':
    main()
