from socket import timeout
import asyncio, logging, sys, time, os
from datetime import  datetime

from os.path import join, dirname
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message


from stk_parser import get_detections, get_stk_token

#TODO remake funtional to OOP
#     try catch
#     change prints to tg_bot module


load_dotenv(join(dirname(__file__),'.env'))
BOT_TOKEN : str = os.environ.get('BOT_TOKEN', '')

dp = Dispatcher()
bot = Bot(BOT_TOKEN)


async def main() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    print('Alive!')

@dp.message(Command(
        'on',
        prefix='/!.',
        ignore_mention=True))
async def now(message: Message, command: CommandObject) -> None:
    token = await get_stk_token()
    new_msg_ = True
    t = command.args
    if t:
        match t[-1]:
            case 'm': # 10m
                timeout = int(t[:-1]) * 60 
                timeout_hint = f'{t} minutes'
            case 'h': # 1h
                timeout = int(t[:-1]) * 60 * 60
                timeout_hint = f'{t} hour'
            case _: # 's' or empty
                timeout = int(t)
                timeout_hint = f'{t} seconds'
    else: 
        timeout = 60
        timeout_hint = '1 minute'
    await bot.send_message(message.chat.id, f'start polling every {timeout_hint}')
    while True:
        status, d = await get_detections(token)
        if status != 200:
            token = await get_stk_token()

            print(f'taken new token: ..{token[:-10]}')
            continue

        match len(d):
            case 0: d_count = 'zero'
            case _: d_count = len(d)

        d_now = f'{datetime.now().strftime("%H:%M:%S")} - {d_count} detections'
        if new_msg_:
            sended = await bot.send_message(message.chat.id, d_now)
            new_msg_ = False
        else:
            if (datetime.now().minute - sended.date.minute) >= 3:
                await bot.delete_message(sended.chat.id, sended.message_id)
                new_msg_ = True
            await bot.edit_message_text(d_now, sended.chat.id, sended.message_id)

            print(datetime.now().minute)
            print(sended.date.minute)
        await asyncio.sleep(timeout) # in seconds


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


