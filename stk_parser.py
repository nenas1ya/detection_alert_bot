import json
import os
from os.path import dirname, join
from typing import Any

import aiohttp
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), verbose=True)
STK_LOGIN = os.environ.get('STK_LOGIN')
STK_PASSWORD = os.environ.get('STK_PASSWORD')
PREMOD_URL = 'http://fku-ural.stk-drive.ru/api/detections/'

async def get_stk_token():

    '''get token from stk api

    :return str: bearer token
    '''

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(
                url='http://fku-ural.stk-drive.ru/api/users/token/',
                data={"username": STK_LOGIN, "password": STK_PASSWORD}
            ) as response:

            return str(json.loads(str(await response.text())).get("access"))


async def get_detections(
            token:str,
            status='AWAITING_VALIDATION',
            created_gte='2024-04-01'
        ) -> list[Any]:
    '''get detections from api

    :param str token: from get_stk_token()
    :param str status: detections which status will be grabed, defaults to 'AWAITING_VALIDATION'
    :param str created_gte: date and greater for detections, defaults to '2024-04-01'
    :return list[Any]: list of detections, every decetction is dict
    '''
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(
                url= f'{PREMOD_URL}?validation_status={status}&created_at__gte={created_gte}T00:00:00.000Z',
                headers={'Authorization': f'Bearer {token}'}
            ) as response:

            res_text = await response.text()

            if response.status != 200:
                # invalid request
                return [response.status, res_text, '']

            data = []
            for el in json.loads(res_text):
                # [{id:created_at}, {..}, ..] from [response with all information]
                data.append({el.get('id'):f'{(el.get("created_at"))[5:-13]}'})

            return [response.status, data, len(data)]
