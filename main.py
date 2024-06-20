import asyncio
import logging
from async_timeout import timeout
from abc import ABC, abstractmethod

from utils import get_envs, DetectionsParser
from bot import TelegramBot

class AbstractMainApp(ABC):
    """
    Abstract base class for the main application.
    """

    def __init__(self):
        self.env_vars = None
        self.parser = None
        self.bot = None
        self.token = None
        self.token_expiration = None

    @abstractmethod
    async def fetch_token(self):
        """
        Abstract method to fetch token, should be implemented in subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def check_detections_periodically(self):
        """
        Abstract method to periodically check detections, should be implemented in subclass.
        """
        pass

    async def initialize(self):
        """
        Initialize environment variables, parser, bot, etc.
        """
        self.env_vars = self.load_env_vars()
        self.parser = self.create_parser()
        self.bot = self.create_bot()

    def load_env_vars(self):
        """
        Load environment variables.
        """

        self.env_vars = get_envs(
            "STK_LOGIN",
            "STK_PASSWORD",
            "DUTSSD_LOGIN",
            "DUTSSD_PASSWORD",
            "DEV_TOKEN",
            "BOT_TOKEN",
        )
        return {
            "STK_LOGIN": "your_stk_login",
            "STK_PASSWORD": "your_stk_password",
            "DUTSSD_LOGIN": "your_dutssd_login",
            "DUTSSD_PASSWORD": "your_dutssd_password",
            "DEV_TOKEN": "your_dev_token",
            "BOT_TOKEN": "your_bot_token",
        }  # Replace with your actual environment variables

    def create_parser(self):
        """
        Create and return an instance of DetectionsParser.
        """
        return DetectionsParser(
            login=self.env_vars["STK_LOGIN"], passw=self.env_vars["STK_PASSWORD"]
        )

    def create_bot(self):
        """
        Create and return an instance of TelegramBot.
        """
        return TelegramBot(self.env_vars["DEV_TOKEN"])

    async def start(self):
        """
        Start the main application.
        """
        await self.initialize()
        await asyncio.gather(self.check_detections_periodically(), self.bot.start())


class MainApp(AbstractMainApp):
    """
    Main application class to handle the periodic checking of detections
    and interfacing with the Telegram bot.
    """

    async def fetch_token(self):
        """
        Fetches the token and renews when expired.
        """
        if (
            self.token_expiration is None
            or self.token_expiration < asyncio.get_event_loop().time()
        ):
            try:
                with timeout(10):
                    self.token = await self.parser.get_token()
                    self.token_expiration = (
                        asyncio.get_event_loop().time() + 3600
                    )  # token lifetime 1 hour
            except asyncio.TimeoutError:
                logging.error("Timeout fetching token")
            except Exception as e:
                logging.error("Error fetching token: %s", e)

    async def check_detections_periodically(self):
        """
        Periodically checks for detections and updates the Telegram bot
        with the current detection count.
        """
        previous_detection_count = {}
        pinned_message_id = {}

        while True:
            try:
                await self.fetch_token()
                new_detections = await self.parser.get_detects(self.token)
                detection_count = len(new_detections)
                chats = self.bot.get_active_chats()

                for chat_id in chats:
                    if detection_count == 0:
                        if previous_detection_count.get(chat_id, 0) > 0:
                            if pinned_message_id.get(chat_id):
                                await self.bot.send_end_of_day_message(chat_id)
                                await self.bot.unpin_message(
                                    chat_id, pinned_message_id[chat_id]
                                )
                                pinned_message_id[chat_id] = None
                        previous_detection_count[chat_id] = 0
                    else:
                        if previous_detection_count.get(chat_id, 0) == 0:
                            message_id = await self.bot.send_detection_message(
                                chat_id, detection_count
                            )
                            pinned_message_id[chat_id] = await self.bot.pin_message(
                                chat_id, message_id
                            )
                        else:
                            await self.bot.edit_detection_message(
                                chat_id, pinned_message_id[chat_id], detection_count
                            )
                        previous_detection_count[chat_id] = detection_count

                await self.bot.update_detections(new_detections)
                self.detections = new_detections
            except Exception as e:
                logging.error("Failed to update detections: %s", e)
            await asyncio.sleep(
                self.bot.get_timeout()
            )  # Adjust the interval dynamically based on settings


if __name__ == "__main__":
    logging.info("Running asyncio from main")
    app = MainApp()
    asyncio.run(app.start())
