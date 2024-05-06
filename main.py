import asyncio
import logging
import os
from datetime import datetime

from classes import CMDLineArguments, DetectionsParser, EnvLoader, TelegramBot


async def main():

    p = CMDLineArguments()
    options = p.parse_args()
    env = EnvLoader()
    if options.dev:
        bot_token = env.get_bot_dev()
    else:
        bot_token = env.get_bot()
    if options.dutssd:
        dutssd = env.get_dutssd()
    else:
        stk = env.get_stk()


if __name__ == "__main__":
    logging.debug("Run asyncio")
    asyncio.run(main())
