import os
import time
import requests
import telegram
import logging
from dotenv import load_dotenv


load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return f'Работу {homework_name} еще не проверили'
    homework_statuses = homework.get('status')
    if homework_statuses == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        raise f'Ошибка при работе с API: {e}'
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():

    while True:
        try:
            logging.debug('Отслеживание статуса запущено')
            send_message(
                parse_homework_status(
                    get_homeworks(1628000000)['homeworks'][0]
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
