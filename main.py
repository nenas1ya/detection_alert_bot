import asyncio
import logging
import os
from datetime import datetime
from pprint import pprint

from classes import CMDLineArguments, DetectionsParser, EnvLoader, TelegramBot


async def main():

    p = CMDLineArguments()
    options = p.parse_args()
    env = EnvLoader()
    x = env.get_all()
    pprint(x)


if __name__ == "__main__":
    logging.info("Run asyncio")
    asyncio.run(main())
