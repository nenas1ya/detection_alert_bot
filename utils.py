import argparse
import asyncio
import logging
import os
from dataclasses import dataclass
from json import loads


from aiohttp import ClientSession as http
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime}.{msecs:0<3.0f} | {levelname:^6} | {funcName:^14} > {message}",
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
    detections_url = f"http://{base_url}/api/detections/"
    token_url = f"http://{base_url}/api/users/token/"

    async def get_token(self) -> str:
        try:
            async with http(trust_env=True) as session:
                async with session.post(
                    url=self.token_url,
                    data={"username": self.login, "password": self.passw},
                ) as response:
                    r_data: dict = loads(str(await response.text()))

                    if response.status == 200:
                        logging.debug(f"Recieved 200")
                    else:
                        raise RuntimeError(
                            f"Bad request [{response.status}] : {r_data}"
                        )

                    if r_data["access"]:
                        return r_data["access"]
                    else:
                        raise ValueError(f"Empty response: {r_data}")

        except Exception as e:
            logging.error(e)
            raise

    async def get_detects(
        self,
        token: str,
        status: str = "AWAITING_VALIDATION",
        created_gte: str = "2024-04-01",
    ) -> list[dict]:
        try:
            async with http(trust_env=True) as session:
                async with session.get(
                    url=f"{self.detections_url}?"
                    f"validation_status={status}&"
                    f"created_at__gte={created_gte}T00:00:00.000Z",
                    headers={"Authorization": f"Bearer {token}"},
                ) as response:
                    r_data: list = loads(str(await response.text()))

                    if response.status == 200:
                        logging.debug(f"Recieved 200")
                    else:
                        raise RuntimeError(
                            f"Bad request [{response.status}] : {r_data}"
                        )
                    if r_data:
                        return r_data
                    else:
                        raise ValueError(f"Empty response: {r_data}")

        except Exception as e:
            logging.error(e)
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
        logging.info("Create cmd argument parser")


def get_envs( *envs: str):
    """STK_LOGIN, STK_PASSWROD
    DUTSSD_LOGIN, DUTSSD_PASSWORD
    DEV_TOKEN,    BOT_TOKEN
    """
    bucket: dict = {}

    load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
    logging.info(f"Load dotenv: {find_dotenv()}")
    for v in envs:

        try:

            var = os.environ.get(v, "?")
            if var == "?":
                raise ValueError(f"No such v in env")
            bucket[v] = var
            logging.debug((f"Get {v}:{var}"))
        except Exception as e:
            logging.error(f"{e} - for '{v}'")
            raise
        finally:
            continue

    if bucket:
        logging.info(f"Get {len(bucket)} envs")
        return bucket
    else:
        raise ValueError("Empty bucket")
