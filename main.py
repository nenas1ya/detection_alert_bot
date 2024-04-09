import time
import asyncio
from datetime import  datetime
from stk_parser import get_detections, get_stk_token

#TODO remake funtional to OOP
#     try catch
#     change prints to tg_bot module


async def main():

    '''take [detections] from stk_parser, manipulate and use tg_bot to send it and'''

    token = await get_stk_token()

    while True:
        status, d = await get_detections(token)
        if status != 200:
            token = await get_stk_token()

            print(f'taken new token: ..{token[:-10]}')

            continue

        print(f'{datetime.now().strftime("%H:%M:%S")} - awaiting {len(d)}')

        await asyncio.sleep(40)

asyncio.run(main())



