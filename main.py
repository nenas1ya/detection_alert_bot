import asyncio
from async_timeout import timeout
import logging
from utils import CMDLineArguments, get_envs, DetectionsParser
from bot import TelegramBot

logging.basicConfig(level=logging.DEBUG)


class MainApp:
    """
    Main application class to handle the periodic checking of detections
    and interfacing with the Telegram bot.
    """

    def __init__(self):
        self.env_vars = None
        self.detections = []
        self.bot = None
        self.parser = None
        self.token = None
        self.token_expiration = None

    async def fetch_token(self):
        """
        Get token and renew when expired
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
                    )  # life time of token 1h
            except asyncio.TimeoutError:
                logging.error("Timeout fetching token")
            except Exception as e:
                logging.error("Error fetching token%s", e)

    async def check_detections_periodically(self):
        """
        Periodically checks for detections and updates the Telegram bot
        with the current detection count.
        """
        previous_detection_count = {}
        pinned_message_id = {}

        while True:
            try:
                token = await self.parser.get_token()
                new_detections = await self.parser.get_detects(token)
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

    async def main(self):
        """
        Main method to initialize environment variables, parser, and bot,
        and start the periodic detection check and bot polling.

        :return: None
        """
        p = CMDLineArguments()

        self.env_vars = get_envs(
            "STK_LOGIN",
            "STK_PASSWORD",
            "DUTSSD_LOGIN",
            "DUTSSD_PASSWORD",
            "DEV_TOKEN",
            "BOT_TOKEN",
        )

        self.parser = DetectionsParser(
            login=self.env_vars["STK_LOGIN"], passw=self.env_vars["STK_PASSWORD"]
        )

        self.bot = TelegramBot(self.env_vars["DEV_TOKEN"])

        await asyncio.gather(self.check_detections_periodically(), self.bot.start())


if __name__ == "__main__":
    logging.info("Run asyncio from main")
    app = MainApp()
    asyncio.run(app.main())
