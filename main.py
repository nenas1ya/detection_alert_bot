import asyncio
import logging
import os
from datetime import datetime
from pprint import pprint

from utils import CMDLineArguments, DetectionsParser, get_envs


async def main():

    p = CMDLineArguments()
    options = p.parse_args()

    get_envs(
        "STK_PASSWORD",
        223,
        "STK_LOGIN",
        "STK_PASSWROD",
        "DUTSSD_LOGIN",
        "DUTSSD_PASSWORD",
        "DEV_TOKEN",
        3,
        "BOT_TOKEN",
    )


if __name__ == "__main__":
    logging.info("Run asyncio from main")
    asyncio.run(main())
