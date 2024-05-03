import argparse
import asyncio
import logging
import os
from datetime import datetime

from dotenv import find_dotenv, load_dotenv

from classes import CMDLineArguments, DetectionsParser, TelegramBot


async def main():
    # load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)

    p = CMDLineArguments()
    options = p.parse_args()

    # logging
    logger = logging.getLogger(__name__)
    logger.setLevel(options.log_level)
    print(options)
    print(logger.level)
    print(f"{os.path.basename(__file__)}")


if __name__ == "__main__":
    asyncio.run(main())
