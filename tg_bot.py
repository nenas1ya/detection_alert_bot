import asyncio
import logging
import sys
import aiogram
import os
from os.path import join, dirname
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv(join(dirname(__file__),'.env'))
BOT_TOKEN : str = os.environ.get('BOT_TOKEN', '')
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(str(message.chat.id))
    print(str(message.chat.id))


async def send_msg(chat_id, text):
    return await bot.send_message(chat_id, text)

async def edit_msg(text, chat_id, message_id):
    await bot.edit_message_text(text, chat_id, message_id)
    
async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

