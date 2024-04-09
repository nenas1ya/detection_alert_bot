import requests
import json
import time
import os
from datetime import date, time, datetime
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__),'.env')
load_dotenv(dotenv_path)
STK_LOGIN = os.environ.get('STK_LOGIN')
STK_PASSWORD = os.environ.get('STK_PASSWORD')
STK_ACCESS_TOKEN = ''
PREMOD_URL = 'http://fku-ural.stk-drive.ru/api/detections/'

def get_stk_token() -> str:
    '''возвращает токен по логин:паролю '''
    return json.loads(
                requests.post(
                    url='http://fku-ural.stk-drive.ru/api/users/token/',
                    data={"username": STK_LOGIN, "password": STK_PASSWORD}
                    ).text
                ).get("access")

def get_detections(token=get_stk_token(), status='AWAITING_VALIDATION',created_gte='2024-03-31') -> list[dict]:
    '''под токеном получает детекции с created_gte даты по настоящее время, возвращает список словарей id:created_at'''
    response = requests.get(
            url= f'{PREMOD_URL}?validation_status={status}&created_at__gte={created_gte}T19:00:00.000Z',
            headers={'Authorization': f'Bearer {token}'},
            verify=False)
    if response.status_code != 200:
        print(response.status_code, response.text, token)
        return response.status_code
    # формирует data [{id: created_at}, ...] из response
    return [{el.get('id'):f'{(el.get("created_at"))[5:-13]}'} for el in json.loads(response.text)] 

if __name__ == "__main__":
    print('from stk_parser.py')
    print(get_detections(get_stk_token()))