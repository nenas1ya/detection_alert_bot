import argparse, asyncio
import logging
import os
from dataclasses import dataclass
from json import loads
from aiohttp import ClientSession
from dotenv import find_dotenv, load_dotenv


logger = logging.getLogger(__name__)


class Config:

    def __init__(self, config=None):
        self.default_config = {
            "Parser": {
                "login": get_envs("STK_LOGIN")[0],
                "password": get_envs("STK_PASSWORD")[0],
                "detections_api": f"http://fku-ural.stk-drive.ru/api/detections/",
                "token_api": f"http://fku-ural.stk-drive.ru/api/users/token/",
                "token_expiration": None,
            },
            "Tg": {"token": get_envs("DEV_TOKEN")[0]},
        }
        self.config = {**self.default_config, **(config or {})}
        self.validate_config()

    def validate_config(self):
        pass


class DetectionsParser():
    """
    A class to handle API interactions for fetching tokens and detections.
    """

    def __init__(self, config=None)
        self.config = config

    async def get_token(self) -> str:
        async with ClientSession(trust_env=True) as session:
            async with session.post(
                url=self.config["token_api"],
                data={
                    "username": self.config["login"],
                    "password": self.config["password"],
                },
            ) as response:
                r_data: dict = loads(await response.text())
                if response.status == 200 and "access" in r_data:
                    logging.debug("Received 200 response")
                    return r_data["access"]
                logging.error("Failed to get token: %s", r_data)
                raise RuntimeError(f"Failed to get token: {r_data}")


    async def fetch_token(self):
        """
        Get token and renew when expired
        """
        if (
            self.config['token_expiration'] is None
            or self.config['token_expiration'] < asyncio.get_event_loop().time()
        ):
            try:
                async with timeout(10):
                    self.token = await self.parser.get_token()
                    self.token_expiration = (
                        asyncio.get_event_loop().time() + 3600
                    )  # life time of token 1h
            except asyncio.TimeoutError:
                logging.error("Timeout fetching token")
            except Exception as e:
                logging.error("Error fetching token%s", e)
                
                
                
    async def get_detects(
        self,
        token: str,
        status: str = "AWAITING_VALIDATION",
        created_gte: str = "2024-04-01",
    ) -> list[dict]:
        async with ClientSession(trust_env=True) as session:
            async with session.get(
                url=f"{self.config['detections_api']}?validation_status={status}&created_at__gte={created_gte}T00:00:00.000Z",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                r_data: list = loads(await response.text())
                if response.status == 200:
                    logging.debug("Received 200 response")
                    return r_data
                logging.error("Failed to get detections: %s", r_data)
                raise RuntimeError(f"Failed to get detections: {r_data}")


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
        level=logging.INFO,
        format="{asctime}.{msecs:0<3.0f} | {levelname:^6} | {funcName:^14} > {message}",
        style="{",
        datefmt="%m-%d %H:%M:%S",
    )
