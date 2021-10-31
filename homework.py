import logging
import os
import time

import requests
import telegram

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot_client = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    '''Проверяем статус и отправляем сообщение'''
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    invalid_response = 'Не удалось получить данные ДЗ. invalid server response'
    verdict = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'approved': 'Ревьюеру всё понравилось, '
                    'можно приступать к следующему уроку.',
        'reviewing': 'Работа взята в ревью'}
    if homework_status == 'reviewing':
        return verdict
    elif homework.get('status') in verdict:
        verdict = verdict[homework.get('status')]
    elif homework_name is None or homework_status is None:
        logging.error(invalid_response)
        return invalid_response
    else:
        logging.error('Неизвестная ошибка. Что-то пошло не так')
        return 'Неизвестная ошибка. Что-то пошло не так'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    current_timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, params=params, headers=headers)
        return homework_statuses.json()
    except Exception as e:
        logging.exception(f'Request raised. Error: {e}')


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Bot down, this type of error did a KO to it: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
