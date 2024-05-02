import asyncio
from datetime import datetime

from classes import Parser

p = Parser()
async def main():
    token = await p.get_token()
    d = await p.get_all_detections(token=token)
    print(len(d))


if __name__ == '__main__':
    print( f'{datetime.now().strftime("%X.%f")[:-3]} | SYS | start from beta main.py')
    asyncio.run(main())
