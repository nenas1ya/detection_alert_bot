
import time
import asyncio
from datetime import  datetime
from stk_parser import get_detections, get_stk_token

#TODO remake funtional to OOP
#     try catch

async def main():
    token = await get_stk_token()
    while True:
        status, d = await get_detections(token)
        if status != 200:
            token = await get_stk_token()
            print(f'new token: ..{token[:-10]}')
            continue
        print(f'{datetime.now().hour}:{datetime.now().minute} - awaiting {len(d)}')
        await asyncio.sleep(40)

asyncio.run(main())



