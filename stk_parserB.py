# STK_PARSER BUT IN CLASSES
import asyncio
from datetime import datetime
from json import loads
import os

from aiohttp import ClientSession as http
from os.path import join, dirname
from dotenv import load_dotenv





class Parser():
    

    def __init__(self) -> None:
        load_dotenv(join(dirname(__file__),'.env'))
        self.login = os.environ.get('STK_LOGIN')
        self.passw = os.environ.get('STK_PASSWORD')
        self.d_url = 'http://fku-ural.stk-drive.ru/api/detections/'
        self.t_url = 'http://fku-ural.stk-drive.ru/api/users/token/'
   
   
    async def get_token(self) -> str:
        async with http(trust_env=True) as session:
            async with session.post(
                url = self.t_url,
                data = {
                    'username': self.login,
                    'password': self.passw
                }
            ) as response:
                if response.status == 200:
                    print(f'{datetime.now().strftime("%X.%f")[:-3]} | 200 | get token')
                    return loads(
                        str(
                            await response.text()
                        )
                    ).get('access')
                else: # Exceptions
                    raise Exception(f'\n{datetime.now().strftime("%H:%M:%S")} | POST {response.status} | get_token:\n'
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
                url=f'{self.d_url}?'
                    f'validation_status={status}&'+
                    f'created_at__gte={created_gte}T00:00:00.000Z',
                headers={
                    'Authorization': f'Bearer {token}'
                }
            ) as response:
                if response.status == 200:
                    print(f'{datetime.now().strftime("%X.%f")[:-3]} | 200 | get detections')
                    return loads(
                        str(
                            await response.text()
                        )
                    )
                else: # Exceptions
                    raise Exception(f'\n{datetime.now().strftime("%H:%M:%S")} | POST {response.status} | get_token:\n'
                                    f'creds    | {self.login}:{self.passw}\n'
                                    f'response | {await response.text()}')

    
    async def get_compact_detections(
            self,
            token: str
    ):
        detections = await self.get_all_detections(token)
        for detection in detections:
            pass
    

async def main():
    p = Parser()
    token = await p.get_token()
    detections = await p.get_all_detections(token=token)
    for d in detections:
        print(d.get('id'))

asyncio.run(main())

