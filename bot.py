from datetime import datetime
import asyncio
import logging
import os
from collections import defaultdict
from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.DEBUG)


class TelegramBot:
    """
    Class to handle Telegram bot functionalities including message handling,
    pinning, unpinning messages and managing settings.
    """

    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.detections = []
        self.pinned_message_id = defaultdict(lambda: None)
        self.chat_settings = defaultdict(lambda: {"timeout": 10, "notify": True})

    async def start(self):
        """
        Initialize the bot with token, dispatcher and settings.
        """
        self.dp.message.register(self.send_welcome, Command(commands=["start"]))
        self.dp.message.register(self.send_help, Command(commands=["help"]))
        self.dp.message.register(self.send_settings, Command(commands=["settings"]))
        self.dp.message.register(self.send_log, Command(commands=["log"]))
        self.dp.message.register(self.ping_api, Command(commands=["ping"]))
        self.dp.message.register(self.set_timeout, Command(commands=["timeout"]))
        self.dp.message.register(self.set_notify, Command(commands=["notify"]))
        

        self.dp.callback_query.register(self.callback_query_handler)

        await self.dp.start_polling(self.bot)

    async def send_welcome(self, message: Message, ):
        """
        Start the bot and set up the message handlers.
        """ 
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Settings", callback_data="settings"),
                    InlineKeyboardButton(text="Ping", callback_data="ping"),
                ],
                [
                    InlineKeyboardButton(text="Help", callback_data="help"),
                    InlineKeyboardButton(text="Log", callback_data="log"),
                ],
            ]
        )
        await message.answer(
            "Hello! I will notify you about detections.",
            reply_markup=keyboard,
        )

    async def callback_query_handler(self, callback_query: CallbackQuery):
        """
        Handle callback queries from inline buttons.
        """
        print("Callback query received:", callback_query.data)
        if callback_query.data == "settings":
            await self.send_settings(callback_query.message)
        elif callback_query.data == "ping":
            await self.ping_api(callback_query.message)
        elif callback_query.data == "help":
            await self.send_help(callback_query.message)
        elif callback_query.data == "log":
            await self.send_log(callback_query.message)
        await callback_query.answer()

    async def send_help(self, message: Message):
        """
        Send help information to the user.
        """
        await message.answer(
            "Available commands:\n/start\n/help\n/settings\n/log\n/ping\n/timeout <seconds>\n/notify <on/off>",
            disable_notification=self.chat_settings[message.chat.id]["notify"],
        )

    async def send_settings(self, message: Message):
        
        settings = self.chat_settings[message.chat.id]
        await message.answer(
            text=f"Current settings:\nTimeout: {settings['timeout']} seconds\nNotifications: {'On' if settings['notify'] else 'Off'}",
            disable_notification=self.chat_settings[message.chat.id]["notify"],
        )

    async def send_log(self, message: Message):
        
        await message.answer(
            "Log is not yet implemented.",
            disable_notification=self.chat_settings[message.chat.id]["notify"],
        )

    async def ping_api(self, message: Message):
       
        await message.answer("Pinging the API...")
        detections_url: str = "http://fku-ural.stk-drive.ru/api/"
        try:
            async with ClientSession() as session:
                start_time = datetime.now()
                async with session.get(detections_url) as response:
                    end_time = datetime.now()
                    ping_time = (end_time - start_time).total_seconds() * 1000
                    response_code = response.status
                    await message.answer(
                        text=f"✅ Ping to {detections_url} returned response code {response_code} in {ping_time:.2f} milliseconds.",
                    )
        except Exception as e:
            logging.error("Failed to ping API: %s", e)
            await message.answer(f"💢 Failed to ping API: {e}")

    async def send_end_of_day_message(self, chat_id):
       
        await self.bot.send_message(
            chat_id=chat_id,
            text="Detections have ended for today.",
            disable_notification=self.chat_settings[chat_id]["notify"],
        )

    async def unpin_message(self, chat_id, message_id):
       
        await self.bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)
        disable_notification = self.chat_settings[chat_id]["notify"]

    async def send_detection_message(self, chat_id, detection_count):
        
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=f"Checked at {self.get_current_time()}, Detections count: {detection_count}",
            disable_notification=self.chat_settings[chat_id]["notify"],
        )
        return message.message_id

    async def edit_detection_message(self, chat_id, message_id, detection_count):
        
        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Checked at {self.get_current_time()}, Detections count: {detection_count}",
        )


    async def pin_message(self, chat_id, message_id):
        
        await self.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=self.chat_settings[chat_id]["notify"],
        )
        return message_id

    async def update_detections(self, detections):
        
        self.detections = detections

    def get_current_time(self):
        
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_active_chats(self):
        
        return list(self.chat_settings.keys())

    def get_timeout(self):
        
        return min(
            [settings["timeout"] for settings in self.chat_settings.values()],
            default=60,
        )

    async def set_timeout(self, message: Message):
        
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
