import asyncio
import logging
from datetime import datetime

from async_timeout import timeout
from bot import TelegramBot
from utils import Config, DetectionsParser, get_envs, setup_logging


class MainApp(Config):
    """
    Main application class to handle the periodic checking of detections
    and interfacing with the Telegram bot.
    """

    def __init__(self, config=None):

        super().__init__(config)
        self.config = {**self.config}

        self.detections = -1
        self.parser = DetectionsParser(self.config["Parser"])

        self.bot = TelegramBot(self.config["Tg"])

    async def check_n_update_detections(self):
        """
        Periodically checks for detections and updates the Telegram bot
        with the current detection count.
        """

        previous_detection_count = 0

        while True:
            try:

                awaiting_detections = await self.parser.fetch_detects(
                    status="AWAITING_VALIDATION",
                )
                invalid_detections = await self.parser.fetch_detects(
                    status="INVALID_DETECTION",
                    created_gte=datetime.now().date(),
                )
                valid_detections = await self.parser.fetch_detects(
                    status="VALID_DETECTION",
                    created_gte=datetime.now().date(),
                )
                self.bot.data["await"] = len(awaiting_detections)
                self.bot.data["invalid"] = len(invalid_detections)
                self.bot.data["valid"] = len(valid_detections)
                await self.bot.update_pin()

                await asyncio.sleep(0.4)
            except Exception as e:
                logging.error("Failed to update detections: %s", e)
                raise


async def main():
    app = MainApp()
    # Start the bot and data updater concurrently
    await asyncio.gather(app.bot.start(), app.check_n_update_detections())


if __name__ == "__main__":
    setup_logging()

    asyncio.run(main())
