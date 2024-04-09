import os
import time
import asyncio
from os.path import join, dirname
from dotenv import load_dotenv
from stk_parser import get_detections



async def check_detections_by_time(seconds_to_wait: int):
    d = await get_detections()
    print(f'awaiting detections: {len(d)}')
    await asyncio.sleep(seconds_to_wait)



while True:
    asyncio.run(check_detections_by_time(60))




