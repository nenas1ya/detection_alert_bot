import os
import time
import asyncio
from os.path import join, dirname
from dotenv import load_dotenv


from stk_parser import get_detections
detects = get_detections()
print(len(detects))


async def check_detections_by_time(t):
    await print(len(get_detections()))
    asyncio.sleep(60)








