import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from utils import get_envs, setup_logging

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, config=None):
        self.config = config
        self.chats = {}
        self.data = {
            "await": 1337,
            "valid": 69,
            "invalid": 228,
            "chars": "‧⁖⁘⁙",
            "c_i": 0,
        }
        self.bot = Bot(
            token=self.config["token"],
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dp = Dispatcher()
        self.setup_handlers()

    def setup_handlers(self):
        @self.dp.message(Command("start"))
        async def command_start_handler(message: Message):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="day stats", callback_data="end_day_stats"
                        )
                    ]
                ]
            )
            await self.bot.send_message(
                message.chat.id,
                f"q = awaiting detections\nc = clicked detections (valid + invalid)",
                reply_markup=keyboard,
            )
            stats_msg = await self.bot.send_message(
                message.chat.id,
                f"<code>q: {self.data['await']} c: {self.data['invalid'] + self.data['valid']}</code>",
            )
            self.chats[message.chat.id] = stats_msg.message_id
            await self.bot.pin_chat_message(stats_msg.chat.id, stats_msg.message_id)
            await self.bot.delete_message(
                chat_id=message.chat.id, message_id=stats_msg.message_id + 1
            )

        @self.dp.callback_query(lambda c: c.data == "end_day_stats")
        async def refresh_callback_handler(callback_query: CallbackQuery):
            await callback_query.answer(text="🍕🍕🍕")
            await self.end_day_stats()

    async def update_pin(self):
        for chat_id in self.chats:
            try:
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=self.chats[chat_id],
                    text=f"<code>q: {self.data['await']} c: {self.data['invalid'] + self.data['valid']} {self.data['chars'][self.data['c_i']]} </code>",
                )
                self.data["c_i"] = 0 if self.data["c_i"] == 3 else self.data["c_i"] + 1
            except Exception as e:
                await print(e)

    async def end_day_stats(self):
        for chat_id in self.chats:
            await self.bot.send_message(
                text=""
                f"\n╭ <i>stats to {str(datetime.now())[-15:-7]}</i>"
                f"\n│  in queue: <code>{self.data['await']}</code>"
                f"\n│   rejected: <code>{self.data['invalid']}</code>"
                f"\n│ approved: <code>{self.data['valid']}</code>"
                f"\n╰  approve: <tg-spoiler>{(self.data['valid'] / (self.data['await'] + self.data['invalid'])  ) * 100:.2f}%</tg-spoiler>",
                chat_id=chat_id,
            )

    async def start(self):
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    setup_logging()
    config = {"token": get_envs("DEV_TOKEN")[0]}
    bot = TelegramBot(config)
    asyncio.run(bot.start())
