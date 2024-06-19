import argparse
import logging
import os
from dataclasses import dataclass
from json import loads
from aiohttp import ClientSession
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime}.{msecs:0<3.0f} | {levelname:^6} | {funcName:^14} > {message}",
    style="{",
    datefmt="%m-%d %H:%M:%S",
)


@dataclass
class DetectionsParser:
    """
    A class to handle API interactions for fetching tokens and detections.
    """

    login: str
    passw: str
    base_url: str = "fku-ural.stk-drive.ru"
    detections_url: str = f"http://{base_url}/api/detections/"
    token_url: str = f"http://{base_url}/api/users/token/"

    async def get_token(self) -> str:
        """
        Fetch an authentication token from the API.
        Returns:
            str: The authentication token.
        """
        async with ClientSession(trust_env=True) as session:
            async with session.post(
                url=self.token_url,
                data={"username": self.login, "password": self.passw},
            ) as response:
                r_data: dict = loads(await response.text())
                if response.status == 200 and "access" in r_data:
                    logging.debug("Received 200 response")
                    return r_data["access"]
                logging.error("Failed to get token: %s", r_data)
                raise RuntimeError(f"Failed to get token: {r_data}")

    async def get_detects(
        self,
        token: str,
        status: str = "AWAITING_VALIDATION",
        created_gte: str = "2024-04-01",
    ) -> list[dict]:
        """
        Fetch detections from the API.
        Args:
            token (str): The authentication token.
            status (str): The status of the detections to fetch.
            created_gte (str): The start date for fetching detections.
        Returns:
            list[dict]: A list of detections.
        """
        async with ClientSession(trust_env=True) as session:
            async with session.get(
                url=f"{self.detections_url}?validation_status={status}&created_at__gte={created_gte}T00:00:00.000Z",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                r_data: list = loads(await response.text())
                if response.status == 200:
                    logging.debug("Received 200 response")
                    return r_data
                logging.error("Failed to get detections: %s", r_data)
                raise RuntimeError(f"Failed to get detections: {r_data}")


class CMDLineArguments(argparse.ArgumentParser):
    """
    A class to handle command-line arguments.
    """

    def __init__(self) -> None:
        super().__init__()
        self.add_argument(
            "-d", "--dev", help="Start with DEV_TOKEN env", action="store_true"
        )
        self.add_argument(
            "--dutssd", help="Fetch dutssd instead stk", action="store_true"
        )


def get_envs(*envs: str) -> dict:
    """
    Load environment variables from a .env file.
    Args:
        envs (str): A list of environment variable names to load.
    Returns:
        dict: A dictionary of environment variables and their values.
    """
    load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
    env_vars = {v: os.environ[v] for v in envs if os.environ.get(v)}
    if len(env_vars) != len(envs):
        missing = set(envs) - env_vars.keys()
        logging.error("Missing environment variables: %s", ", ".join(missing))
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    logging.info("Loaded %d environment variables", len(env_vars))
    return env_vars
