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
PREMOD_URL = 'http://fku-ural.stk-drive.ru/api/detections/premoderation-room/'
VALIDATION_STATUS = 'VALID_DETECTION'
# while True:
STK_ACCESS_TOKEN = json.loads(
    requests.post(
        url='http://fku-ural.stk-drive.ru/api/users/token/',
        data={"username": STK_LOGIN, "password": STK_PASSWORD}
        ).text
    ).get("access")

res = json.loads(
    requests.get(
        url= f'{PREMOD_URL}?validation_status={VALIDATION_STATUS}&created_at__gte=2024-04-03T19:00:00.000Z&created_at__lte=2024-04-30T18:59:59.999Z',
        headers={'Authorization': f'Bearer {STK_ACCESS_TOKEN}'},
        verify=False
    ).text
)
data = []
for el in res:
    data.append(
        {el.get('id'):f'{(el.get("created_at"))[5:-13]}'}
    )
print(len(res))
print(data[0],data[int(len(data)/2)],data[len(data)-1])
#   time.sleep(5)
