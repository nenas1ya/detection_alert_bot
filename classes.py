import asyncio
import os
import sys
import aiogram
import logging

from dataclasses import dataclass
from datetime import datetime
from json import loads

import aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent, Message)
from aiohttp import ClientSession as http
from dotenv import find_dotenv, load_dotenv

load_dotenv(
    find_dotenv('.envb', raise_error_if_not_found=True),
    verbose=True)

@dataclass
class Parser():

    login: str
    passw: str
    detections_url = 'http://fku-ural.stk-drive.ru/api/detections/'
    token_url = 'http://fku-ural.stk-drive.ru/api/users/token/'


    async def get_token(
            self,
            stk_login: str = '') -> str:
        async with http(trust_env=True) as session:
            async with session.post(
                url = self.token_url,
                data = {
                    'username': self.login,
                    'password': self.passw
                }
            ) as response:
                if response.status == 200:
                    print(f'{datetime.now().strftime("%X.%f")[:-3]} | STK | get token')
                    return loads(
                        str(
                            await response.text()
                        )
                    ).get('access')
                else: # Exceptions
                    raise Exception(f'\n{datetime.now().strftime("%X.%f")[:-3]} | STK | get_token {response.status} :\n'
                                    f'creds    | {self.login}:{self.passw}\n'
                                    f'response | {await response.text()}')


    async def get_all_detections(
            self,
            token: str,
            status: str = 'AWAITING_VALIDATION',
            created_gte: str ='2024-04-01'
        ) -> list[dict]:
        async with http(trust_env=True) as session:
            async with session.get(
                url=f'{self.detections_url}?'
                    f'validation_status={status}&'+
                    f'created_at__gte={created_gte}T00:00:00.000Z',
                headers={
                    'Authorization': f'Bearer {token}'
                }
            ) as response:
                if response.status == 200:
                    print(f'{datetime.now().strftime("%X.%f")[:-3]} | STK | get detections')
                    return loads(
                        str(
                            await response.text()
                        )
                    )
                else: # Exceptions
                    raise Exception(f'{datetime.now().strftime("%X.%f")[:-3]} | STK | get_detections{response.status}:\n'
                                    f'    | creds: {self.login}:{self.passw}\n'
                                    f'    | resp: {await response.text()}')


class TelegramBot():
    def __init__(self) -> None:
        pass

    async def connect(self):
        BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
        print(len(BOT_TOKEN))
        bot = aiogram.Bot(BOT_TOKEN)

    async def create_dispatcher(self):
        pass
    async def start_handler(self):
        pass
