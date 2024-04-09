
import time
import asyncio
from os.path import join, dirname
from dotenv import load_dotenv
from stk_parser import get_detections, get_stk_token



async def check_detections_by_time(seconds_to_wait: int, token=None):
    d = await get_detections(token=token)
    print(f'awaiting detections: {len(d)}')
    await asyncio.sleep(seconds_to_wait)



while True:
    token = asyncio.run(get_stk_token())
    asyncio.run(check_detections_by_time(60, token))


# TODO:
# change token forwarding


