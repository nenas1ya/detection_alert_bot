import asyncio
import logging
from datetime import datetime
from async_timeout import timeout
from utils import DetectionsParser, Config, get_envs, setup_logging
from bot import TelegramBot


class MainApp(Config):
    """
    Main application class to handle the periodic checking of detections
    and interfacing with the Telegram bot.
    """

    def __init__(self, config=None):

        super().__init__(config)
        self.config = {**self.config}

        self.detections = []
        self.parser = DetectionsParser(self.config["Parser"])

        self.bot = TelegramBot(self.config["Tg"]['token'])


    async def check_detections_periodically(self):
        """
        Periodically checks for detections and updates the Telegram bot
        with the current detection count.
        """
        previous_detection_count = 0
        pinned_message_id = {}

        while True:
            try:
                await self.fetch_token()

                awaiting_detections = await self.parser.get_detects(
                    self.token,
                    status="AWAITING_VALIDATION",
                )
                invalid_detections = await self.parser.get_detects(
                    self.token,
                    status="INVALID_DETECTION",
                    created_gte=datetime.now().date(),
                )
                valid_detections = await self.parser.get_detects(
                    self.token,
                    status="VALID_DETECTION",
                    created_gte=datetime.now().date(),
                )

                aw_detection_count = len(awaiting_detections)
                inv_detection_count = len(invalid_detections)
                val_detection_count = len(valid_detections)
                chats = list(self.bot.chat_settings.keys())
                for chat_id in chats:
                    if aw_detection_count == 0:
                        if previous_detection_count > 0 and pinned_message_id.get(
                            chat_id
                        ):
                            await self.bot.send_end_of_day_message(chat_id)
                            await self.bot.unpin_message(
                                chat_id, pinned_message_id[chat_id]
                            )
                            pinned_message_id[chat_id] = None
                        previous_detection_count = 0
                    else:
                        if previous_detection_count == 0:
                            message_id = await self.bot.send_detection_message(
                                chat_id, aw_detection_count
                            )
                            pinned_message_id[chat_id] = await self.bot.pin_message(
                                chat_id, message_id
                            )
                        else:
                            await self.bot.edit_detection_message(
                                chat_id, pinned_message_id[chat_id], aw_detection_count
                            )
                        previous_detection_count = aw_detection_count
                    self.detections = awaiting_detections
                    await asyncio.sleep(self.bot.get_timeout(chat_id))
            except Exception as e:
                logging.error("Failed to update detections: %s", e)
                raise Exception from e

    def set_config(self):
        pass

    async def main(self):
        """
        Main method to initialize environment variables, parser, and bot,
        and start the periodic detection check and bot polling.

        :return: None
        """
        self.env_vars = get_envs(
            "STK_LOGIN",
            "STK_PASSWORD",
            "DUTSSD_LOGIN",
            "DUTSSD_PASSWORD",
            "DEV_TOKEN",
            "BOT_TOKEN",
        )


if __name__ == "__main__":
    setup_logging()
    app = MainApp()
    await app.run()
