
import time
import asyncio
from datetime import  datetime
from os.path import join, dirname
from dotenv import load_dotenv
from stk_parser import get_detections, get_stk_token



async def main():
    token = await get_stk_token()
    while True:
        d = await get_detections(token)
        if type(d) == int:
            print(d)
            token = await get_stk_token()
            print(f'new token: {token}')
            continue
        print(f'{datetime.now().hour}:{datetime.now().minute} - awaiting {len(d)}')
        await asyncio.sleep(40)

asyncio.run(main())

# TODO:
# change token forwarding


