import argparse
import asyncio
import logging
import os
from datetime import datetime

from dotenv import find_dotenv, load_dotenv

from classes import Parser


async def main():

    print( f'{datetime.now().strftime("%X.%f")[:-3]} | SYS | start from beta main.py')



    # command-line arguments
    parser = argparse.ArgumentParser(

    )
    parser.add_argument('--log-level',
                           default='INFO',
                           choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))

    parser.add_argument('--test-bot')
    options = parser.parse_args()

    # logging
    logging.basicConfig(
        format='%(levelname)s %(name)s %(message)s',
        level=options.log_level
    )
    logger = logging.getLogger(__name__)



    print(logger.level)
    print(f'{os.path.basename(__file__)}')


if __name__ == '__main__':




    asyncio.run(main())
