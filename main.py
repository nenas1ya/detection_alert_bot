import asyncio
import logging
import os
from datetime import datetime
from pprint import pprint

from utils import CMDLineArguments, DetectionsParser, EnvLoader



async def main():

    p = CMDLineArguments()
    options = p.parse_args()
    env = EnvLoader()
    login,passw = env.get_stk().values()
    d = DetectionsParser(login,passw)
    print(await d.get_token())
if __name__ == "__main__":
    logging.info("Run asyncio")
    asyncio.run(main())
