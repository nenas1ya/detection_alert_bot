import asyncio, logging, sys, time, os
from datetime import  datetime

from os.path import join, dirname
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from stk_parser import get_detections, get_stk_token

#TODO remake funtional to OOP
#     try catch
#     change prints to tg_bot module


load_dotenv(join(dirname(__file__),'.env'))
BOT_TOKEN : str = os.environ.get('BOT_TOKEN', '')
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    token = await get_stk_token()
    print('Alive!')
    while True:
        status, d = await get_detections(token)
        if status != 200:
            token = await get_stk_token()

            print(f'taken new token: ..{token[:-10]}')

            continue

        print(len(d))
        match len(d):
            case 0: d_count = 'нет'
            case _: d_count = len(d)

        d_now = f'{datetime.now().strftime("%H:%M:%S")} - {d_count} детекций'
        if not message:
            message = await send_msg(message.chat.id, d_now)
        else:
            await edit_msg(d_now, message.chat.id, message.message_id)
        await asyncio.sleep(30)


async def send_msg(chat_id, text):
    return await bot.send_message(chat_id, text)

async def edit_msg(text, chat_id, message_id):
    await bot.edit_message_text(text, chat_id, message_id)

CHAT_ID = '4109809726'
    # 6359870347 my DM
    # 4109809726 test group


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


