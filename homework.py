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
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_statuses = homework.get('status')
    if homework_name is None or homework_statuses is None:
        raise TGBotException('Сообщение не содержит обязательных полей')   
    if homework_statuses == 'reviewing':
        verdict = 'Работа взята в ревью.'
    elif homework_statuses == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_statuses == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    else:
        raise TGBotException('Значение поля заполнено неверно')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    

def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
    except requests.exceptions.RequestException:
        raise TGBotException('Ошибка при работе с API')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise TGBotException('Ошибка при работе с сервером')
    answer = homework_statuses.json()
    return answer


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            logging.debug('Отслеживание статуса запущено')          
            new_homework = get_homeworks(current_timestamp)
            current_timestamp = new_homework.get('current_date')           
            if 'homeworks' not in new_homework:
                raise TGBotException('Список не существует')
            last_homework = new_homework['homeworks']
            if last_homework != []:
                send_message(parse_homework_status(last_homework[0]))
            else:
                raise TGBotException('Список пуст')             
            logging.info('Бот отправил сообщение')
            time.sleep(15 * 60)
        except Exception as e:
            error_message = f'Бот упал с ошибкой: {e}'
            logging.error(error_message)
            bot.send_message(chat_id=CHAT_ID, text=error_message)
            time.sleep(15)


if __name__ == '__main__':
    main()
