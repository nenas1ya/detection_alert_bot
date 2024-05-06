import argparse
import asyncio
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from json import loads

import aiogram
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiohttp import ClientSession as http
from dotenv import find_dotenv, load_dotenv


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime}.{msecs:0<3.0f}   | {levelname:6} | {funcName:^14} > {message}",
    style="{",
    datefmt="%m-%d %H:%M:%S",
)


@dataclass
class DetectionsParser:

    login: str
    passw: str
    base_url: str = (
        "fku-ural.stk-drive.ru"  # dutssd.admtyumen.ru | fku-ural.stk-drive.ru
    )
    detections_url = f"http://{base_url}api/detections/"
    token_url = f"http://{base_url}/api/users/token/"

    async def get_token(self, stk_login: str = "") -> str:
        async with http(trust_env=True) as session:
            async with session.post(
                url=self.token_url,
                data={"username": self.login, "password": self.passw},
            ) as response:
                if response.status == 200:
                    logging.debug(f"Recieved api token")
                    return loads(str(await response.text())).get("access")
                else:
                    logging.error(
                        f"Bad request:\n{response.status}:{await response.text()}"
                    )
                    raise Exception("Bad request")

    async def get_all_detections(
        self,
        token: str,
        status: str = "AWAITING_VALIDATION",
        created_gte: str = "2024-04-01",
    ) -> list[dict]:
        async with http(trust_env=True) as session:
            async with session.get(
                url=f"{self.detections_url}?"
                f"validation_status={status}&"
                + f"created_at__gte={created_gte}T00:00:00.000Z",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                if response.status == 200:
                    logging.debug(f"Recieved {status} from {created_gte} detections")
                    return loads(str(await response.text()))
                else:
                    logging.error(
                        f"Bad request:\n{response.status}:{await response.text()}"
                    )
                    raise Exception("Bad request")


class TelegramBot:
    def __init__(self) -> None:
        pass

    async def connect(self):
        pass

    async def create_dispatcher(self):
        pass

    async def start_handler(self):
        pass


class CMDLineArguments(argparse.ArgumentParser):

    def __init__(self) -> None:
        super().__init__()

        self.add_argument(
            "-d", "--dev", help="Start with DEV_TOKEN env", action="store_true"
        )
        self.add_argument(
            "--dutssd", help="Fetch dutssd instead stk", action="store_true"
        )
        logging.debug("Cmd argument parser")


class EnvLoader:

    def __init__(self) -> None:
        try:
            load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
            logging.info(f"Load dotenv: {find_dotenv()}")
        except Exception as e:
            logging.error(f"Cant load dotenv: {e}")
            raise e.with_traceback(None)

    def get_stk(self):

        if os.environ.get("STK_LOGIN") and os.environ.get("STK_PASSWORD"):
            logging.info("Get STK env variables")
            return {
                "STK_LOGIN": os.environ.get("STK_LOGIN"),
                "STK_PASSWORD": os.environ.get("STK_PASSWORD"),
            }
        else:
            logging.error(f"Cant load STK env variables")
            raise Exception("Value STK_LOGIN, STK_PASSWORD is None")

    def get_dutssd(self):

        if os.environ.get("DUTSSD_LOGIN") and os.environ.get("DUTSSD_PASSWORD"):
            logging.info("Get DUTSSD env variables")
            return {
                "DUTSSD_LOGIN": os.environ.get("DUTSSD_LOGIN"),
                "DUTSSD_PASSWORD": os.environ.get("DUTSSD_PASSWORD"),
            }
        else:
            logging.error(f"Cant load DUTSSD env variables")
            raise Exception("Value DUTSSD_LOGIN, DUTSSD_PASSWORD is None")

    def get_bot_dev(self):


        if os.environ.get("DEV_TOKEN"):
            logging.info("Get DEV_TOKEN token")
            return {"DEV_TOKEN": os.environ.get("DEV_TOKEN")}
        else:
            logging.error(f"Cant load DEV_TOKEN env variables")
            raise Exception("Value DEV_TOKEN is None")

    def get_bot(self):

        if os.environ.get("BOT_TOKEN"):
            logging.info("Get BOT_TOKEN token")
            return {"BOT_TOKEN": os.environ.get("BOT_TOKEN")}
        else:
            logging.error(f"Cant load BOT_TOKEN env variables")
            raise Exception("Value BOT_TOKEN is None")