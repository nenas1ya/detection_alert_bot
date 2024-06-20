from datetime import datetime
import asyncio
import logging
import os
from collections import defaultdict
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
logging.basicConfig(level=logging.DEBUG)


class TelegramBot:
    """
    Class to handle Telegram bot functionalities including message handling,
    pinning, unpinning messages and managing settings.
    """

    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.detections = []
        self.pinned_message_id = defaultdict(lambda: None)
        self.chat_settings = defaultdict(lambda: {"timeout": 60, "notify": True})

    async def start(self):
        """
        Initialize the bot with token, dispatcher and settings.

        :param str bot_token: The bot token for authenticating with the Telegram API.
        """
        self.dp.message(Command("start"))(self.send_welcome)
        self.dp.message(Command("help"))(self.send_help)
        self.dp.message(Command("settings"))(self.send_settings)
        self.dp.message(Command("log"))(self.send_log)
        self.dp.message(Command("ping"))(self.ping_api)
        self.dp.message(Command("timeout"))(self.set_timeout)
        self.dp.message(Command("notify"))(self.set_notify)
        await self.dp.start_polling(self.bot)

    async def send_welcome(self, message: Message):
        """
        Start the bot and set up the message handlers.
        """
        await message.answer("Hello! I will notify you about detections.")

    async def send_help(self, message: Message):
        """
        Send help information to the user.
        """
        await message.answer(
            "Available commands:\n/start\n/help\n/settings\n/log\n/ping\n/timeout <seconds>\n/notify <on/off>"
        )

    async def send_settings(self, message: Message):
        """
        Send the current settings to the user.
        """
        chat_id = message.chat.id
        settings = self.chat_settings[chat_id]
        await message.answer(
            f"Current settings:\nTimeout: {settings['timeout']} seconds\nNotifications: {'On' if settings['notify'] else 'Off'}"
        )

    async def send_log(self, message: Message):
        """
        Send the log to the user.
        """
        await message.answer("Log is not yet implemented.")

    async def ping_api(self, message: Message):
        """
        Ping the API and respond to the user.
        """
        await message.answer("Pinging the API...")

    async def send_end_of_day_message(self, chat_id):
        """
        Send a message indicating detections have ended for the day.
        """
        await self.bot.send_message(
            chat_id=chat_id, text="Detections have ended for today."
        )

    async def unpin_message(self, chat_id, message_id):
        """
        Unpin a message in the chat.

        :param int chat_id: The chat ID where the message is pinned.
        :param int message_id: The message ID to unpin.
        """
        await self.bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)

    async def send_detection_message(self, chat_id, detection_count):
        """
        Send a message with the current detection count.

        :param int chat_id: The chat ID to send the message to.
        :param int detection_count: The current count of detections.
        :return: int: The message ID of the sent message.
        """
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=f"Checked at {self.get_current_time()}, Detections count: {detection_count}",
        )
        return message.message_id

    async def edit_detection_message(self, chat_id, message_id, detection_count):
        """
        Edit a previously sent message with the updated detection count.

        :param int chat_id: The chat ID where the message is sent.
        :param int message_id: The message ID to edit.
        :param int detection_count: The updated count of detections.
        """
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Checked at {self.get_current_time()}, Detections count: {detection_count}",
        )

    async def pin_message(self, chat_id, message_id):
        """
        Pin a message in the chat.

        :param int chat_id: The chat ID where the message is sent.
        :param int message_id: The message ID to pin.
        :return: int: The message ID of the pinned message.
        """
        await self.bot.pin_chat_message(chat_id=chat_id, message_id=message_id)
        return message_id

    async def update_detections(self, detections):
        """
        Update the detections list.

        :param list detections: The list of new detections.
        """
        self.detections = detections

    def get_current_time(self):
        """
        Get the current time as a formatted string.

        :return: str: The current time in 'YYYY-MM-DD HH:MM:SS' format.
        """

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_active_chats(self):
        """
        Get a list of active chat IDs.

        :return: list: A list of active chat IDs.
        """
        return list(self.chat_settings.keys())

    def get_timeout(self):
        """
        Get the minimum timeout setting from all active chats.

        :return: int: The minimum timeout in seconds.
        """
        return min(
            [settings["timeout"] for settings in self.chat_settings.values()],
            default=60,
        )

    async def set_timeout(self, message: Message):
        """
        Set the timeout setting for the chat.

        :param Message message: The incoming message from a user.
        """
        chat_id = message.chat.id
        try:
            _, timeout = message.text.split()
            timeout = int(timeout)
            self.chat_settings[chat_id]["timeout"] = timeout
            await message.answer(f"Timeout has been set to {timeout} seconds.")
        except Exception as e:
            logging.error("Failed to set timeout: %s", e)
            await message.answer("Usage: /timeout <seconds>")

    async def set_notify(self, message: Message):
        """
        Set the notification preference for the chat.

        :param Message message: The incoming message from a user.
        """
        chat_id = message.chat.id
        try:
            _, notify = message.text.split()
            notify = notify.lower() == "on"
            self.chat_settings[chat_id]["notify"] = notify
            await message.answer(
                f"Notifications have been turned {'on' if notify else 'off'}."
            )
        except ValueError:
            await message.answer("Invalid notification value. Usage: /notify <on/off>")
        except IndexError:
            await message.answer(
                "Notification value is missing. Usage: /notify <on/off>"
            )
        except Exception as e:
            logging.error("Failed to set notifications: %s", e)
            await message.answer("An error occurred. Please try again.")


if __name__ == "__main__":
    bot_token = os.getenv("BOT_TOKEN")
    asyncio.run(TelegramBot(bot_token).start())
