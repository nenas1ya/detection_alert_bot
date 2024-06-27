import argparse
import asyncio
import logging
import os
from json import loads

from aiohttp import ClientSession
from async_timeout import timeout
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, config=None):
        self.default_config = {
            "Parser": {
                "login": get_envs("STK_LOGIN")[0],
                "password": get_envs("STK_PASSWORD")[0],
                "detections_api": "http://fku-ural.stk-drive.ru/api/detections/",
                "token": None,
                "token_api": "http://fku-ural.stk-drive.ru/api/users/token/",
                "token_expiration": None,
            },
            "Tg": {"token": get_envs("DEV_TOKEN")[0], "timeout": 5},
        }
        self.config = {**self.default_config, **(config or {})}
        self.validate_config()

    def validate_config(self):
        pass


class DetectionsParser:
    """
    A class to handle API interactions for fetching tokens and detections.
    """

    def __init__(self, config=None):
        self.config = config

    async def fetch_detects(
        self,
        status: str = "AWAITING_VALIDATION",
        created_gte: str = "2024-04-01",
    ) -> list[dict]:

        current_time = asyncio.get_event_loop().time()
        if (
            self.config["token"] is None
            or self.config["token_expiration"] is None
            or self.config["token_expiration"] < current_time
        ):
            try:
                async with timeout(10):
                    async with ClientSession() as session:
                        async with session.post(
                            url=self.config["token_api"],
                            data={
                                "username": self.config["login"],
                                "password": self.config["password"],
                            },
                        ) as response:
                            r_data: dict = loads(await response.text())
                            if response.status == 200 and "access" in r_data:
                                logging.info("Response 200")
                                logging.debug("r_data: %s", r_data)
                                self.config["token"] = r_data["access"]
                                self.config["token_expiration"] = current_time + 3600
                            else:
                                logging.error(
                                    "Failed to get token: %s", response.content
                                )

            except asyncio.TimeoutError:
                logging.error("Timeout while fetching token")
                raise
            except Exception as e:
                logging.error("Error while fetching token: %s", str(e))
                raise e
        else:
            logging.info("Using cashed token")
        try:
            async with timeout(10):
                async with ClientSession() as session:
                    async with session.get(
                        url=f"{self.config['detections_api']}?validation_status={status}&created_at__gte={created_gte}T00:00:00.000Z",
                        headers={"Authorization": f"Bearer {self.config['token']}"},
                    ) as response:

                        r_data: list = loads(await response.text())
                        if response.status == 200:
                            logging.debug("Response 200")
                            return r_data
                        logging.error("Failed to get detections: %s", r_data)

        except asyncio.TimeoutError:
            logging.error("Timeout while fetching detections")
            raise
        except Exception as e:
            logging.error("Error while fetching detections: %s", str(e))
            raise


class CMDLineArguments(argparse.ArgumentParser):
    def __init__(self) -> None:
        super().__init__()
        self.add_argument(
            "-d", "--dev", help="Start with DEV_TOKEN env", action="store_true"
        )
        self.add_argument(
            "--dutssd", help="Fetch dutssd instead stk", action="store_true"
        )


def get_envs(*envs: str) -> dict:
    load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
    return [
        (
            os.environ[v]
            if (os.environ.get(v) and v in os.environ)
            else logging.error("Missing environment variable: %s", v) or None
        )
        for v in envs
    ]


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="{asctime}.{msecs:0<3.0f} | {levelname:^6} | {funcName:^14} > {message}",
        style="{",
        datefmt="%m-%d %H:%M:%S",
    )
