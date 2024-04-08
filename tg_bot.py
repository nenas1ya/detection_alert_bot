import asyncio
import aiogram
import os
from os.path import join, dirname
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import Command
from aiogram.types import Message

BOT_TOKEN = os.environ.get('BOT_TOKEN')


def main():
    pass



if __name__ == '__main__':
    print("\t> live")
    asyncio.run(main())
