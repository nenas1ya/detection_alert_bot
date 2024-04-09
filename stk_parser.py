import aiohttp
import asyncio
import json
from datetime import datetime
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

async def get_stk_token() -> str:
    '''возвращает токен по логин:паролю '''
    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.post(
                url='http://fku-ural.stk-drive.ru/api/users/token/',
                data={"username": STK_LOGIN, "password": STK_PASSWORD}
            ) as response:
            return json.loads(str(await response.text())).get("access")
    

async def get_detections(token=None, status='AWAITING_VALIDATION',created_gte='2024-03-31') -> list[dict]:
    '''под токеном получает детекции с created_gte даты по настоящее время, возвращает список словарей id:created_at'''
    if not token:
        token = await get_stk_token()
        print(datetime.now(), 'new token taken')

    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.get(
                url= f'{PREMOD_URL}?validation_status={status}&created_at__gte={created_gte}T19:00:00.000Z',
                headers={'Authorization': f'Bearer {token}'}
            ) as response:
            if response.status != 200:
                print(response.status, await response.text(), token)
                return response.status
            # формирует data [{id: created_at}, ...] из response
            print(datetime.now().hour, datetime.now().minute, sep=':',end=' ')
            return [{el.get('id'):f'{(el.get("created_at"))[5:-13]}'} for el in json.loads(await response.text())] 

    
if __name__ == "__main__":
    print('from stk_parser.py')
    d = asyncio.run(get_detections())
    print(len(d))
    