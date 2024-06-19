import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

logging.basicConfig(level=logging.DEBUG)


class TelegramBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.detections = []

    async def start(self):
        self.dp.message(Command("start"))(self.send_welcome)
        self.dp.message(Command("detections"))(self.send_detections)
        await self.dp.start_polling(self.bot)

    async def send_welcome(self, message: Message):
        await message.answer("Hello! I will notify you about detections.")

    async def send_detections(self, message: Message):
        if self.detections:
            detection_messages = "\n".join(
                [
                    f"Detection ID: {d['id']} - Status: {d['validation_status']}"
                    for d in self.detections
                ]
            )
            await message.answer(f"Detections:\n{detection_messages}")
        else:
            await message.answer("No detections found.")

    async def update_detections(self, detections):
        self.detections = detections
        # Additional logic to send notifications about new detections can be added here
